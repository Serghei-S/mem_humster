from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

import cv2
import numpy as np
import torch
from PIL import Image, ImageOps
from transformers import CLIPModel, CLIPProcessor

from hamster_reference_data import (
    FACE_FEATURE_ORDER,
    FACE_FEATURE_WEIGHTS,
    IGNORED_REFERENCE_FILENAMES,
    PROMPTS,
    get_reference_detail,
    get_reference_expression_profile,
    get_reference_traits,
)


SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
FACE_PADDING = 0.35
GEOMETRY_WEIGHT = 0.74
GEOMETRY_SEMANTIC_WEIGHT = 0.18
GEOMETRY_DESCRIPTION_WEIGHT = 0.08
FALLBACK_SEMANTIC_WEIGHT = 0.12
FALLBACK_DESCRIPTION_WEIGHT = 0.40
FALLBACK_VISUAL_WEIGHT = 0.48
MODEL_NAME = "openai/clip-vit-base-patch32"

FACE_FEATURE_LABELS: dict[str, str] = {
    "mouth_open": "Рот открыт",
    "mouth_round": "Губы округлены",
    "smile": "Улыбка",
    "sadness": "Грусть",
    "eye_open": "Глаза раскрыты",
    "brow_raise": "Брови вверх",
    "brow_frown": "Брови хмурятся",
    "asymmetry": "Перекос лица",
}

FACE_CUE_LABELS: dict[str, str] = {
    "mouth_open": "рот открыт",
    "mouth_round": "губы округлены",
    "smile": "улыбка",
    "sadness": "грусть",
    "eye_open": "глаза широко",
    "brow_raise": "брови подняты",
    "brow_frown": "брови нахмурены",
    "asymmetry": "выражение перекошено",
}

FACE_CUE_THRESHOLDS: dict[str, float] = {
    "mouth_open": 0.18,
    "mouth_round": 0.14,
    "smile": 0.18,
    "sadness": 0.18,
    "eye_open": 0.45,
    "brow_raise": 0.16,
    "brow_frown": 0.16,
    "asymmetry": 0.18,
}


@dataclass(frozen=True)
class PromptScore:
    label: str
    score: float


@dataclass(frozen=True)
class ReferenceImage:
    filename: str
    label: str
    description: str
    traits: tuple[str, ...]
    dominant_prompt: str
    top_prompts: tuple[PromptScore, ...]
    profile: np.ndarray
    image_embedding: np.ndarray
    description_embedding: np.ndarray
    expression_profile: np.ndarray


class HamsterMatcher:
    def __init__(self, project_dir: Path) -> None:
        self.project_dir = project_dir
        self.reference_paths = tuple(
            sorted(
                path
                for path in project_dir.iterdir()
                if path.is_file()
                and path.name not in IGNORED_REFERENCE_FILENAMES
                and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
            )
        )
        if not self.reference_paths:
            raise ValueError("Не нашел референсных картинок хомяков в корне проекта.")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        if self.face_detector.empty():
            raise RuntimeError("Не удалось загрузить каскад для детекции лица.")

        self.prompt_texts = [text for text, _ in PROMPTS]
        self.prompt_labels = [label for _, label in PROMPTS]
        self.face_feature_weights = np.array(
            [FACE_FEATURE_WEIGHTS[name] for name in FACE_FEATURE_ORDER],
            dtype=np.float32,
        )
        self.model = CLIPModel.from_pretrained(MODEL_NAME).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(MODEL_NAME, use_fast=False)
        self.model.eval()
        self.logit_scale = float(self.model.logit_scale.exp().item())
        self.text_features = self._encode_texts(self.prompt_texts)
        self.references = tuple(self._build_reference(path) for path in self.reference_paths)

    def list_references(self) -> list[dict[str, object]]:
        return [
            {
                "filename": reference.filename,
                "label": reference.label,
                "description": reference.description,
                "traits": list(reference.traits),
                "image_url": f"/reference/{reference.filename}",
                "dominant_prompt": reference.dominant_prompt,
                "top_prompts": [score.__dict__ for score in reference.top_prompts],
            }
            for reference in self.references
        ]

    def match(
        self,
        frame: Image.Image,
        face_features: Mapping[str, float] | None = None,
    ) -> dict[str, object]:
        prepared_frame, face_found = self._prepare_frame(frame)
        frame_profile, frame_embedding = self._encode_image(prepared_frame)
        frame_face_features = self._normalize_face_features(face_features)
        face_geometry_found = frame_face_features is not None

        ranked: list[dict[str, object]] = []
        for reference in self.references:
            semantic_similarity = self._profile_similarity(frame_profile, reference.profile)
            description_similarity = self._embedding_similarity(
                frame_embedding,
                reference.description_embedding,
            )
            visual_similarity = self._embedding_similarity(
                frame_embedding,
                reference.image_embedding,
            )

            if face_geometry_found:
                geometry_similarity = self._face_geometry_similarity(
                    frame_face_features,
                    reference.expression_profile,
                )
                score = (
                    GEOMETRY_WEIGHT * geometry_similarity
                    + GEOMETRY_SEMANTIC_WEIGHT * semantic_similarity
                    + GEOMETRY_DESCRIPTION_WEIGHT * description_similarity
                )
                score_breakdown = {
                    "face_geometry": float(round(geometry_similarity, 4)),
                    "semantic": float(round(semantic_similarity, 4)),
                    "description": float(round(description_similarity, 4)),
                }
            else:
                score = (
                    FALLBACK_SEMANTIC_WEIGHT * semantic_similarity
                    + FALLBACK_DESCRIPTION_WEIGHT * description_similarity
                    + FALLBACK_VISUAL_WEIGHT * visual_similarity
                )
                score_breakdown = {
                    "semantic": float(round(semantic_similarity, 4)),
                    "description": float(round(description_similarity, 4)),
                    "visual": float(round(visual_similarity, 4)),
                }

            ranked.append(
                {
                    "filename": reference.filename,
                    "label": reference.label,
                    "description": reference.description,
                    "traits": list(reference.traits),
                    "image_url": f"/reference/{reference.filename}",
                    "dominant_prompt": reference.dominant_prompt,
                    "top_prompts": [score_item.__dict__ for score_item in reference.top_prompts],
                    "score": float(round(score, 4)),
                    "score_breakdown": score_breakdown,
                }
            )

        ranked.sort(key=lambda item: item["score"], reverse=True)

        if face_geometry_found:
            current_expression = [
                score.__dict__ for score in self._describe_face_features(frame_face_features)
            ]
            current_features = self._face_feature_payload(frame_face_features)
            analysis_mode = "face_geometry"
        else:
            current_expression = [
                score.__dict__ for score in self._top_prompt_scores(frame_profile)
            ]
            current_features = []
            analysis_mode = "clip_fallback"

        return {
            "face_found": face_found,
            "face_geometry_found": face_geometry_found,
            "analysis_mode": analysis_mode,
            "current_expression": current_expression,
            "current_features": current_features,
            "best_match": ranked[0],
            "alternatives": ranked[1:4],
        }

    def _build_reference(self, image_path: Path) -> ReferenceImage:
        detail = get_reference_detail(image_path.name)
        traits = get_reference_traits(image_path.name)
        with Image.open(image_path) as image:
            prepared = self._prepare_reference_image(image)
        profile, image_embedding = self._encode_image(prepared)
        top_prompts = self._top_prompt_scores(profile)
        description_embedding = self._encode_texts(
            [self._compact_description_text(detail.label, detail.description, traits)]
        )[0].detach().cpu().numpy()
        expression_profile = self._expression_profile_to_array(
            get_reference_expression_profile(image_path.name)
        )
        return ReferenceImage(
            filename=image_path.name,
            label=detail.label,
            description=detail.description,
            traits=traits,
            dominant_prompt=top_prompts[0].label,
            top_prompts=tuple(top_prompts),
            profile=profile,
            image_embedding=image_embedding,
            description_embedding=description_embedding,
            expression_profile=expression_profile,
        )

    def _prepare_reference_image(self, image: Image.Image) -> Image.Image:
        image = ImageOps.exif_transpose(image).convert("RGBA")
        alpha_bbox = image.getchannel("A").getbbox()
        if alpha_bbox:
            image = image.crop(alpha_bbox)

        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        composited = Image.alpha_composite(background, image).convert("RGB")
        return self._square_pad(composited)

    def _prepare_frame(self, frame: Image.Image) -> tuple[Image.Image, bool]:
        frame = ImageOps.exif_transpose(frame).convert("RGB")
        frame_array = np.array(frame)
        bgr_frame = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
        gray_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(
            gray_frame,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(90, 90),
        )

        if len(faces) == 0:
            return self._center_square_crop(frame), False

        x, y, width, height = max(faces, key=lambda item: item[2] * item[3])
        padding_x = int(width * FACE_PADDING)
        padding_y = int(height * FACE_PADDING)
        left = max(x - padding_x, 0)
        top = max(y - padding_y, 0)
        right = min(x + width + padding_x, frame.width)
        bottom = min(y + height + padding_y, frame.height)
        cropped = frame.crop((left, top, right, bottom))
        return self._square_pad(cropped), True

    def _encode_texts(self, prompt_texts: Iterable[str]) -> torch.Tensor:
        inputs = self.processor(
            text=list(prompt_texts),
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.model.config.text_config.max_position_embeddings,
        )
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with torch.inference_mode():
            features = self.model.get_text_features(**inputs)
        return self._normalize_tensor(features)

    def _encode_image(self, image: Image.Image) -> tuple[np.ndarray, np.ndarray]:
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with torch.inference_mode():
            features = self.model.get_image_features(**inputs)
        features = self._normalize_tensor(features)
        profile = torch.softmax((features @ self.text_features.T) * self.logit_scale, dim=-1)
        return (
            self._normalize_numpy(profile[0].detach().cpu().numpy()),
            features[0].detach().cpu().numpy(),
        )

    def _top_prompt_scores(self, profile: np.ndarray, limit: int = 3) -> list[PromptScore]:
        indexed_scores = sorted(
            enumerate(profile.tolist()),
            key=lambda item: item[1],
            reverse=True,
        )[:limit]
        return [
            PromptScore(label=self.prompt_labels[index], score=round(score, 4))
            for index, score in indexed_scores
        ]

    def _describe_face_features(
        self,
        face_features: np.ndarray,
        limit: int = 4,
    ) -> list[PromptScore]:
        feature_map = self._face_feature_dict(face_features)
        active_cues = [
            PromptScore(label=FACE_CUE_LABELS[name], score=float(round(value, 4)))
            for name, value in feature_map.items()
            if value >= FACE_CUE_THRESHOLDS[name]
        ]
        active_cues.sort(key=lambda item: item.score, reverse=True)

        if active_cues:
            return active_cues[:limit]

        neutral_score = float(round(max(0.0, 1.0 - np.mean(face_features) * 1.6), 4))
        return [PromptScore(label="выражение почти нейтральное", score=neutral_score)]

    def _face_feature_payload(self, face_features: np.ndarray) -> list[dict[str, object]]:
        feature_map = self._face_feature_dict(face_features)
        return [
            {
                "name": name,
                "label": FACE_FEATURE_LABELS[name],
                "score": float(round(value, 4)),
            }
            for name, value in feature_map.items()
        ]

    def _face_feature_dict(self, face_features: np.ndarray) -> dict[str, float]:
        return {
            feature_name: float(face_features[index])
            for index, feature_name in enumerate(FACE_FEATURE_ORDER)
        }

    def _normalize_face_features(
        self,
        face_features: Mapping[str, float] | None,
    ) -> np.ndarray | None:
        if not face_features:
            return None

        values = [
            self._clamp_score(face_features.get(feature_name, 0.0))
            for feature_name in FACE_FEATURE_ORDER
        ]
        if max(values, default=0.0) < 0.03:
            return None
        return np.array(values, dtype=np.float32)

    def _expression_profile_to_array(self, profile: Mapping[str, float]) -> np.ndarray:
        return np.array(
            [self._clamp_score(profile.get(feature_name, 0.0)) for feature_name in FACE_FEATURE_ORDER],
            dtype=np.float32,
        )

    def _face_geometry_similarity(
        self,
        face_features: np.ndarray,
        reference_profile: np.ndarray,
    ) -> float:
        deltas = np.abs(face_features - reference_profile)
        per_feature_match = np.clip(1.0 - deltas, 0.0, 1.0)
        weighted_score = float(np.average(per_feature_match, weights=self.face_feature_weights))
        return round(weighted_score, 6)

    def _embedding_similarity(self, left: np.ndarray, right: np.ndarray) -> float:
        return float(np.clip((float(np.dot(left, right)) + 1.0) / 2.0, 0.0, 1.0))

    def _profile_similarity(self, left: np.ndarray, right: np.ndarray) -> float:
        return float(np.clip(float(np.dot(left, right)), 0.0, 1.0))

    def _square_pad(self, image: Image.Image) -> Image.Image:
        size = max(image.width, image.height)
        canvas = Image.new("RGB", (size, size), "white")
        offset = ((size - image.width) // 2, (size - image.height) // 2)
        canvas.paste(image, offset)
        return canvas

    def _center_square_crop(self, image: Image.Image) -> Image.Image:
        side = min(image.width, image.height)
        left = (image.width - side) // 2
        top = (image.height - side) // 2
        cropped = image.crop((left, top, left + side, top + side))
        return self._square_pad(cropped)

    def _compact_description_text(
        self,
        label: str,
        description: str,
        traits: tuple[str, ...],
    ) -> str:
        traits_text = ", ".join(traits[:3])
        words = f"{label}. {traits_text}. {description}".split()
        return " ".join(words[:18])

    def _clamp_score(self, value: object) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        return float(np.clip(numeric, 0.0, 1.0))

    def _normalize_tensor(self, tensor: torch.Tensor) -> torch.Tensor:
        return tensor / tensor.norm(dim=-1, keepdim=True)

    def _normalize_numpy(self, array: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(array)
        if norm == 0:
            return array
        return array / norm
