from __future__ import annotations

import base64
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel

from hamster_matcher import HamsterMatcher


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


class FramePayload(BaseModel):
    image: str
    face_features: dict[str, float] | None = None


def decode_data_url(data_url: str) -> bytes:
    if "," in data_url:
        _, encoded = data_url.split(",", 1)
    else:
        encoded = data_url
    try:
        return base64.b64decode(encoded)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Не удалось декодировать кадр с камеры.") from error


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.matcher = HamsterMatcher(BASE_DIR)
    yield


app = FastAPI(
    title="Hamster Mirror",
    description="Подбирает ближайшего хомяка по выражению лица с камеры.",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/references")
async def get_references() -> dict[str, object]:
    matcher: HamsterMatcher = app.state.matcher
    return {"references": matcher.list_references()}


@app.get("/reference/{filename}")
async def get_reference(filename: str) -> FileResponse:
    file_path = (BASE_DIR / filename).resolve()
    if file_path.parent != BASE_DIR.resolve() or not file_path.exists():
        raise HTTPException(status_code=404, detail="Картинка не найдена.")
    return FileResponse(file_path)


@app.post("/api/match")
async def match_frame(payload: FramePayload) -> dict[str, object]:
    matcher: HamsterMatcher = app.state.matcher
    raw_frame = decode_data_url(payload.image)

    try:
        with Image.open(BytesIO(raw_frame)) as image:
            frame = image.convert("RGB")
    except (UnidentifiedImageError, OSError) as error:
        raise HTTPException(status_code=400, detail="Кадр не удалось прочитать как изображение.") from error

    return matcher.match(frame, face_features=payload.face_features)
