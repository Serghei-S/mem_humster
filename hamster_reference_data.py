from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReferenceDetail:
    label: str
    description: str


IGNORED_REFERENCE_FILENAMES = {"contact_sheet.png"}

PROMPTS: tuple[tuple[str, str], ...] = (
    ("a calm neutral expression with closed mouth", "спокойный покерфейс"),
    ("a blank numb face with no visible emotion", "пустой взгляд"),
    ("a sleepy bored face with half closed eyes", "сонный прищур"),
    ("a shy timid face", "застенчивый вид"),
    ("a tiny closed-mouth smile", "маленькая улыбка"),
    ("a warm blushing smile", "улыбка с румянцем"),
    ("a cute innocent face", "милое невинное лицо"),
    ("a happy face with a wide open smile", "широкая радость"),
    ("a laughing face", "смех"),
    ("a face screaming with mouth wide open", "истеричный крик"),
    ("a crying face with dramatic sadness", "рыдание"),
    ("a pleading sad face", "жалобный взгляд"),
    ("a shocked face with a small round mouth", "шок с круглым ртом"),
    ("a shocked face with bulging eyes", "выпученный шок"),
    ("a goofy face with the tongue out", "язык наружу"),
    ("a drooling ecstatic face", "слюнявый восторг"),
    ("a suspicious side-eye", "косой подозрительный взгляд"),
    ("a judging face with one eyebrow raised", "осуждающая бровь"),
    ("a smug sly grin", "самодовольная ухмылка"),
    ("a furious angry face", "злость"),
    ("a hush gesture with a finger on the lips", "жест тише"),
    ("a nerdy face with glasses", "очкарик"),
    ("a lovestruck face making a heart gesture", "влюблённый восторг"),
    ("a peaceful face listening to music", "спокойствие под музыку"),
    ("a mischievous devilish grin", "чёртиковая улыбка"),
    ("an exhausted face melting from heat", "изнеможение от жары"),
    ("a dramatic traumatized face", "драматичный надлом"),
    ("an old wise stern face", "старческая мудрость"),
)


REFERENCE_DETAILS: dict[str, ReferenceDetail] = {
    "sticker.webp": ReferenceDetail(
        label="Истеричный крик со слюной",
        description=(
            "Голова запрокинута, рот распахнут почти на все лицо, торчат два передних "
            "зуба, глаза щурятся от безумного смеха, а вниз тянется голубая слюна."
        ),
    ),
    "sticker2.webp": ReferenceDetail(
        label="Тише, ни звука",
        description=(
            "Хомяк приложил палец к губам, глаза округлены, рот почти закрыт, а вся поза "
            "настойчиво требует молчания."
        ),
    ),
    "sticker3.webp": ReferenceDetail(
        label="Расслабленная слюнявая лыба",
        description=(
            "Глаза закрыты от удовольствия, рот открыт маленьким черным треугольником, "
            "а изо рта тянется тонкая полоска слюны."
        ),
    ),
    "sticker4.webp": ReferenceDetail(
        label="Глотка на максимум",
        description=(
            "Рот раскрыт вертикально, язык вытянут далеко вниз, глаза влажные и "
            "напряженные, будто это крик на самом пределе."
        ),
    ),
    "sticker5.webp": ReferenceDetail(
        label="Дурашливый восторг с языком",
        description=(
            "Глаза закатились вверх, рот распахнут, язык свисает почти до груди, а лицо "
            "выглядит как чистое безумное веселье."
        ),
    ),
    "sticker6.webp": ReferenceDetail(
        label="Разбитое сердце на фоне бури",
        description=(
            "На фоне пустой серый двор и большая надпись про любовь, а сам хомяк внизу "
            "смотрит прямо с каменным печальным ртом."
        ),
    ),
    "sticker7.webp": ReferenceDetail(
        label="Примитивный немой шок",
        description=(
            "Мордочка сведена к точечным глазам и овальному черному рту, все выражение "
            "держится на чистом простом удивлении."
        ),
    ),
    "sticker8.webp": ReferenceDetail(
        label="Скепсис с поднятой бровью",
        description=(
            "Одна бровь резко задрана вверх, взгляд косой и недоверчивый, рот слегка "
            "приоткрыт, будто хомяк не верит ни единому слову."
        ),
    ),
    "sticker9.webp": ReferenceDetail(
        label="Пыхтящая злость",
        description=(
            "Брови сведены, рот раскрыт кривой черной пастью, по бокам клубы пара, "
            "и весь хомяк кипит от раздражения."
        ),
    ),
    "sticker10.webp": ReferenceDetail(
        label="Паника с выпученными глазами",
        description=(
            "Глаза вылезают наружу как трубы, рот превращен в огромную черную пропасть, "
            "а нижняя губа обвисает от чистого ужаса."
        ),
    ),
    "sticker11.webp": ReferenceDetail(
        label="Влюбленный жест сердечком",
        description=(
            "Хомяк сложил лапки в сердечко, вокруг летают розовые сердечки, глаза "
            "блестят, а рот открыт в счастливой восторженной улыбке."
        ),
    ),
    "sticker12.webp": ReferenceDetail(
        label="Зажатая тревожная гримаса",
        description=(
            "Брови сведены домиком, глаза прищурены, рот сжался в неровную темную "
            "скобку, будто хомяк еле сдерживает неловкость или слезы."
        ),
    ),
    "sticker13.webp": ReferenceDetail(
        label="Рыдающий вой",
        description=(
            "Лоб собран морщинами, рот открыт вниз дугой и уходит в темноту, словно "
            "хомяк одновременно плачет и воет."
        ),
    ),
    "sticker14.webp": ReferenceDetail(
        label="Жалобный щенячий взгляд",
        description=(
            "Огромные печальные глаза подняты вверх, рот вытянут маленькой дугой вниз, "
            "и весь силуэт выглядит беспомощно и очень грустно."
        ),
    ),
    "sticker15.webp": ReferenceDetail(
        label="Настороженное оцепенение",
        description=(
            "Глаза широко раскрыты и смотрят прямо, рот слегка приоткрыт, а на лице нет "
            "ни радости ни гнева, только пустая настороженность."
        ),
    ),
    "sticker16.webp": ReferenceDetail(
        label="Смущенная улыбка с пухлыми щеками",
        description=(
            "Щеки раздуты и ярко розовеют, глаза блестят, а рот собран в маленькую "
            "довольную улыбку."
        ),
    ),
    "sticker17.webp": ReferenceDetail(
        label="Уставший умник с блокнотом",
        description=(
            "Полуприкрытые глаза, очки сползли на нос, в лапах блокнот и ручка, а лицо "
            "выглядит как у измученного преподавателя."
        ),
    ),
    "sticker18.webp": ReferenceDetail(
        label="Нерд в квадратных очках",
        description=(
            "Толстые квадратные очки, легкая зубастая улыбка и поднятый палец, как будто "
            "хомяк сейчас объяснит всем очевидную вещь."
        ),
    ),
    "sticker19.webp": ReferenceDetail(
        label="Болезненная обида",
        description=(
            "Нос покраснел, под глазами слезы, рот дрожит маленькой дугой, а выражение "
            "похоже на обиду и простудную слабость сразу."
        ),
    ),
    "sticker20.webp": ReferenceDetail(
        label="Драматичный боковой разворот",
        description=(
            "Пол-лица утопает в черной тени, голова повернута вбок, взгляд тяжелый и "
            "пустой, будто кадр из мрачной манги."
        ),
    ),
    "sticker21.webp": ReferenceDetail(
        label="Жесткий косой прищур",
        description=(
            "Брови резко наклонены, глаза смотрят исподлобья, рот вытянут в тонкую "
            "линию, и все лицо выражает раздраженное осуждение."
        ),
    ),
    "sticker22.webp": ReferenceDetail(
        label="Детский восторг с леденцом",
        description=(
            "На голове разноцветная шапка с пропеллером, язык высунут, перед лицом "
            "огромный круглый леденец, а выражение чисто детское и безумно радостное."
        ),
    ),
    "sticker23.webp": ReferenceDetail(
        label="Комично скорбная физиономия",
        description=(
            "Лоб наморщен, щеки свисают, рот растянут широкой печальной складкой, будто "
            "хомяк уже собрался трагически расплакаться."
        ),
    ),
    "sticker24.webp": ReferenceDetail(
        label="Добродушный профессор",
        description=(
            "Круглые очки, тонкая улыбка, тяжелые щеки и двойной подбородок создают "
            "образ уверенного и снисходительного мудреца."
        ),
    ),
    "sticker25.webp": ReferenceDetail(
        label="Боевой визг в ушанке",
        description=(
            "На голове зеленая ушанка со звездой, глаза зажмурены от крика, рот раскрыт "
            "на все лицо, видны зубы и полоска голубой слюны."
        ),
    ),
    "sticker26.webp": ReferenceDetail(
        label="Абсолютный покерфейс",
        description=(
            "Щелочки вместо глаз, рот едва намечен, наружу торчит один зуб, а весь "
            "корпус неподвижен и почти лишен эмоций."
        ),
    ),
    "sticker27.webp": ReferenceDetail(
        label="Счастливый рот до ушей",
        description=(
            "Над головой висит цепочка как кудри или гирлянда, рот огромный и идеально "
            "овальный, а лицо светится беззаботной радостью."
        ),
    ),
    "sticker28.webp": ReferenceDetail(
        label="Суровый старец в лодке",
        description=(
            "Хомяк с седой бородой сидит за деревянным бортом рядом с веслом, глаза "
            "усталые и строгие, настроение мрачной мудрости."
        ),
    ),
    "sticker29.webp": ReferenceDetail(
        label="Тихое самодовольство",
        description=(
            "Глаза почти закрыты, брови высоко подняты, щеки поджаты вверх, а легкая "
            "улыбка выдает довольную собой ухмылку."
        ),
    ),
    "sticker30.webp": ReferenceDetail(
        label="Нежная застенчивая улыбка",
        description=(
            "Щеки порозовели, маленький язык высунут совсем чуть-чуть, а рот собран в "
            "круглую мягкую улыбку."
        ),
    ),
    "sticker31.webp": ReferenceDetail(
        label="Чертовски довольный",
        description=(
            "Красные рожки, хвост со стрелкой и вилы по бокам, язык слегка высунут, а "
            "улыбка самодовольная и игривая."
        ),
    ),
    "sticker32.webp": ReferenceDetail(
        label="Спокойно слушает музыку",
        description=(
            "На ушах наушники, рядом плавают музыкальные ноты, рот расслаблен, а взгляд "
            "мягкий и умиротворенный."
        ),
    ),
    "sticker33.webp": ReferenceDetail(
        label="Плавится от жары",
        description=(
            "Сверху светит палящее солнце, по морде и телу текут капли, рот открыт в "
            "измученном крике, выражение полного перегрева."
        ),
    ),
    "sticker34.webp": ReferenceDetail(
        label="Невинность на фоне безумия",
        description=(
            "Спереди маленькая спокойная мордочка с точечными глазами и крошечной "
            "улыбкой, а сзади полупрозрачный орущий двойник."
        ),
    ),
    "sticker35.webp": ReferenceDetail(
        label="Коллективная истерика",
        description=(
            "В кадре бесконечное поле одинаково орущих хомяков с распахнутыми ртами и "
            "зубами, настроение массового безумного восторга."
        ),
    ),
    "sticker36.webp": ReferenceDetail(
        label="Хитрая боковая ухмылка",
        description=(
            "Один глаз прищурен, второй смотрит в сторону, а рот изогнут в тонкую "
            "хищную улыбку с явным самодовольством."
        ),
    ),
    "sticker37.webp": ReferenceDetail(
        label="Получил по голове",
        description=(
            "Сверху летят красные предметы, на голове и щеке кровавые пятна, а лицо "
            "застыло в шоковой пустоте."
        ),
    ),
    "sticker38.webp": ReferenceDetail(
        label="Безумный зубастый экстаз",
        description=(
            "Глаза выпучены огромными шарами, рот растянут в квадратный оскал с "
            "гигантскими зубами, выражение нелепого восторга."
        ),
    ),
}


def get_reference_detail(filename: str) -> ReferenceDetail:
    detail = REFERENCE_DETAILS.get(filename)
    if detail is not None:
        return detail

    stem = Path(filename).stem.replace("_", " ")
    return ReferenceDetail(
        label=stem,
        description="Мемный хомяк без ручного описания. Сравнение строится по выражению лица и общей позе.",
    )


FEATURE_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("слюн",), "слюна"),
    (("язык",), "язык наружу"),
    (("очки",), "очки"),
    (("блокнот", "ручк"), "блокнот"),
    (("сердечк",), "сердечки"),
    (("леден",), "леденец"),
    (("ушанк", "звезд"), "ушанка"),
    (("рожк",), "рожки"),
    (("хвост",), "хвост"),
    (("вилы",), "вилы"),
    (("наушник", "музык", "ноты"), "музыка"),
    (("бород", "старец"), "борода"),
    (("пропеллер",), "шапка с пропеллером"),
    (("лодк", "весл", "борт"), "лодка"),
    (("тень",), "черная тень"),
    (("пар",), "пар"),
    (("солнц", "жар", "капл"), "жара"),
    (("толпа", "бесконечн", "поле"), "толпа"),
    (("кровав",), "кровь"),
    (("зуб",), "зубы"),
    (("щек", "румян", "розове"), "румяные щеки"),
    (("бров",), "поднятые брови"),
    (("косой", "прищур", "исподлоб"), "косой взгляд"),
    (("крик", "визг", "вой", "распахнут"), "крик"),
    (("шок", "ужас", "выпуч"), "шок"),
    (("печаль", "слез", "рыдан", "груст", "жалоб", "обид"), "грусть"),
    (("улыб", "ухмыл"), "улыбка"),
    (("смех", "радост", "восторг"), "восторг"),
)


def get_reference_traits(filename: str) -> tuple[str, ...]:
    detail = get_reference_detail(filename)
    text = f"{detail.label} {detail.description}".lower()
    traits: list[str] = []

    for keywords, trait in FEATURE_RULES:
        if any(keyword in text for keyword in keywords) and trait not in traits:
            traits.append(trait)

    if not traits:
        traits.append(detail.label.lower())

    return tuple(traits[:5])


FACE_FEATURE_ORDER: tuple[str, ...] = (
    "mouth_open",
    "mouth_round",
    "smile",
    "sadness",
    "eye_open",
    "brow_raise",
    "brow_frown",
    "asymmetry",
)

FACE_FEATURE_WEIGHTS: dict[str, float] = {
    "mouth_open": 1.6,
    "mouth_round": 0.9,
    "smile": 1.4,
    "sadness": 1.2,
    "eye_open": 1.2,
    "brow_raise": 0.9,
    "brow_frown": 1.0,
    "asymmetry": 0.8,
}

EXPRESSION_PRESETS: dict[str, dict[str, float]] = {
    "scream_drool": {
        "mouth_open": 1.0,
        "mouth_round": 0.25,
        "smile": 0.35,
        "sadness": 0.0,
        "eye_open": 0.30,
        "brow_raise": 0.45,
        "brow_frown": 0.05,
        "asymmetry": 0.0,
    },
    "scream_vertical": {
        "mouth_open": 1.0,
        "mouth_round": 0.35,
        "smile": 0.10,
        "sadness": 0.0,
        "eye_open": 0.45,
        "brow_raise": 0.55,
        "brow_frown": 0.15,
        "asymmetry": 0.0,
    },
    "tongue_scream": {
        "mouth_open": 1.0,
        "mouth_round": 0.18,
        "smile": 0.45,
        "sadness": 0.0,
        "eye_open": 0.50,
        "brow_raise": 0.45,
        "brow_frown": 0.05,
        "asymmetry": 0.0,
    },
    "hush": {
        "mouth_open": 0.05,
        "mouth_round": 0.10,
        "smile": 0.05,
        "sadness": 0.0,
        "eye_open": 0.55,
        "brow_raise": 0.20,
        "brow_frown": 0.15,
        "asymmetry": 0.0,
    },
    "panic": {
        "mouth_open": 0.95,
        "mouth_round": 0.35,
        "smile": 0.0,
        "sadness": 0.15,
        "eye_open": 1.0,
        "brow_raise": 0.80,
        "brow_frown": 0.15,
        "asymmetry": 0.0,
    },
    "heart_happy": {
        "mouth_open": 0.50,
        "mouth_round": 0.15,
        "smile": 0.95,
        "sadness": 0.0,
        "eye_open": 0.65,
        "brow_raise": 0.40,
        "brow_frown": 0.0,
        "asymmetry": 0.0,
    },
    "sad_tense": {
        "mouth_open": 0.12,
        "mouth_round": 0.18,
        "smile": 0.0,
        "sadness": 0.78,
        "eye_open": 0.45,
        "brow_raise": 0.55,
        "brow_frown": 0.20,
        "asymmetry": 0.0,
    },
    "crying": {
        "mouth_open": 0.55,
        "mouth_round": 0.45,
        "smile": 0.0,
        "sadness": 1.0,
        "eye_open": 0.30,
        "brow_raise": 0.70,
        "brow_frown": 0.35,
        "asymmetry": 0.0,
    },
    "pleading_sad": {
        "mouth_open": 0.12,
        "mouth_round": 0.20,
        "smile": 0.0,
        "sadness": 0.95,
        "eye_open": 0.85,
        "brow_raise": 0.82,
        "brow_frown": 0.10,
        "asymmetry": 0.0,
    },
    "blank_alert": {
        "mouth_open": 0.10,
        "mouth_round": 0.22,
        "smile": 0.0,
        "sadness": 0.05,
        "eye_open": 0.75,
        "brow_raise": 0.30,
        "brow_frown": 0.08,
        "asymmetry": 0.0,
    },
    "soft_smile": {
        "mouth_open": 0.10,
        "mouth_round": 0.08,
        "smile": 0.75,
        "sadness": 0.0,
        "eye_open": 0.55,
        "brow_raise": 0.15,
        "brow_frown": 0.0,
        "asymmetry": 0.0,
    },
    "nerd_tired": {
        "mouth_open": 0.05,
        "mouth_round": 0.10,
        "smile": 0.08,
        "sadness": 0.10,
        "eye_open": 0.22,
        "brow_raise": 0.03,
        "brow_frown": 0.10,
        "asymmetry": 0.0,
    },
    "nerd_smile": {
        "mouth_open": 0.08,
        "mouth_round": 0.08,
        "smile": 0.55,
        "sadness": 0.0,
        "eye_open": 0.50,
        "brow_raise": 0.08,
        "brow_frown": 0.0,
        "asymmetry": 0.0,
    },
    "side_eye": {
        "mouth_open": 0.05,
        "mouth_round": 0.05,
        "smile": 0.05,
        "sadness": 0.0,
        "eye_open": 0.38,
        "brow_raise": 0.30,
        "brow_frown": 0.55,
        "asymmetry": 0.85,
    },
    "childish_delight": {
        "mouth_open": 0.32,
        "mouth_round": 0.08,
        "smile": 0.88,
        "sadness": 0.0,
        "eye_open": 0.55,
        "brow_raise": 0.15,
        "brow_frown": 0.0,
        "asymmetry": 0.0,
    },
    "neutral_poker": {
        "mouth_open": 0.02,
        "mouth_round": 0.03,
        "smile": 0.02,
        "sadness": 0.0,
        "eye_open": 0.18,
        "brow_raise": 0.0,
        "brow_frown": 0.05,
        "asymmetry": 0.0,
    },
    "wise_neutral": {
        "mouth_open": 0.05,
        "mouth_round": 0.05,
        "smile": 0.12,
        "sadness": 0.08,
        "eye_open": 0.22,
        "brow_raise": 0.03,
        "brow_frown": 0.08,
        "asymmetry": 0.0,
    },
    "open_laugh": {
        "mouth_open": 0.75,
        "mouth_round": 0.15,
        "smile": 0.92,
        "sadness": 0.0,
        "eye_open": 0.25,
        "brow_raise": 0.12,
        "brow_frown": 0.0,
        "asymmetry": 0.0,
    },
    "smug": {
        "mouth_open": 0.04,
        "mouth_round": 0.04,
        "smile": 0.82,
        "sadness": 0.0,
        "eye_open": 0.30,
        "brow_raise": 0.18,
        "brow_frown": 0.18,
        "asymmetry": 0.48,
    },
    "music_calm": {
        "mouth_open": 0.04,
        "mouth_round": 0.06,
        "smile": 0.25,
        "sadness": 0.0,
        "eye_open": 0.45,
        "brow_raise": 0.0,
        "brow_frown": 0.0,
        "asymmetry": 0.0,
    },
    "heat_meltdown": {
        "mouth_open": 0.82,
        "mouth_round": 0.28,
        "smile": 0.0,
        "sadness": 0.55,
        "eye_open": 0.32,
        "brow_raise": 0.25,
        "brow_frown": 0.18,
        "asymmetry": 0.0,
    },
    "innocent_smile": {
        "mouth_open": 0.02,
        "mouth_round": 0.02,
        "smile": 0.35,
        "sadness": 0.0,
        "eye_open": 0.50,
        "brow_raise": 0.0,
        "brow_frown": 0.0,
        "asymmetry": 0.0,
    },
    "toothy_shock": {
        "mouth_open": 0.35,
        "mouth_round": 0.10,
        "smile": 0.62,
        "sadness": 0.0,
        "eye_open": 1.0,
        "brow_raise": 0.65,
        "brow_frown": 0.0,
        "asymmetry": 0.0,
    },
    "stunned_hurt": {
        "mouth_open": 0.08,
        "mouth_round": 0.12,
        "smile": 0.0,
        "sadness": 0.28,
        "eye_open": 0.55,
        "brow_raise": 0.18,
        "brow_frown": 0.10,
        "asymmetry": 0.0,
    },
    "angry": {
        "mouth_open": 0.62,
        "mouth_round": 0.18,
        "smile": 0.0,
        "sadness": 0.05,
        "eye_open": 0.42,
        "brow_raise": 0.02,
        "brow_frown": 1.0,
        "asymmetry": 0.0,
    },
    "broken_heart": {
        "mouth_open": 0.04,
        "mouth_round": 0.16,
        "smile": 0.0,
        "sadness": 0.82,
        "eye_open": 0.32,
        "brow_raise": 0.22,
        "brow_frown": 0.12,
        "asymmetry": 0.0,
    },
    "drool_relaxed": {
        "mouth_open": 0.18,
        "mouth_round": 0.06,
        "smile": 0.32,
        "sadness": 0.0,
        "eye_open": 0.08,
        "brow_raise": 0.0,
        "brow_frown": 0.0,
        "asymmetry": 0.0,
    },
}

REFERENCE_EXPRESSION_PRESETS: dict[str, str] = {
    "sticker.webp": "scream_drool",
    "sticker2.webp": "hush",
    "sticker3.webp": "drool_relaxed",
    "sticker4.webp": "scream_vertical",
    "sticker5.webp": "tongue_scream",
    "sticker6.webp": "broken_heart",
    "sticker7.webp": "blank_alert",
    "sticker8.webp": "side_eye",
    "sticker9.webp": "angry",
    "sticker10.webp": "panic",
    "sticker11.webp": "heart_happy",
    "sticker12.webp": "sad_tense",
    "sticker13.webp": "crying",
    "sticker14.webp": "pleading_sad",
    "sticker15.webp": "blank_alert",
    "sticker16.webp": "soft_smile",
    "sticker17.webp": "nerd_tired",
    "sticker18.webp": "nerd_smile",
    "sticker19.webp": "sad_tense",
    "sticker20.webp": "broken_heart",
    "sticker21.webp": "side_eye",
    "sticker22.webp": "childish_delight",
    "sticker23.webp": "sad_tense",
    "sticker24.webp": "nerd_smile",
    "sticker25.webp": "scream_drool",
    "sticker26.webp": "neutral_poker",
    "sticker27.webp": "open_laugh",
    "sticker28.webp": "wise_neutral",
    "sticker29.webp": "smug",
    "sticker30.webp": "soft_smile",
    "sticker31.webp": "smug",
    "sticker32.webp": "music_calm",
    "sticker33.webp": "heat_meltdown",
    "sticker34.webp": "innocent_smile",
    "sticker35.webp": "scream_drool",
    "sticker36.webp": "smug",
    "sticker37.webp": "stunned_hurt",
    "sticker38.webp": "toothy_shock",
}

REFERENCE_EXPRESSION_OVERRIDES: dict[str, dict[str, float]] = {
    "sticker8.webp": {"smile": 0.0, "asymmetry": 0.72},
    "sticker20.webp": {"eye_open": 0.22, "brow_raise": 0.30},
    "sticker21.webp": {"brow_frown": 0.75, "asymmetry": 0.75},
    "sticker24.webp": {"smile": 0.32, "eye_open": 0.30},
    "sticker29.webp": {"smile": 0.68, "brow_raise": 0.45, "asymmetry": 0.18},
    "sticker31.webp": {"smile": 0.88, "mouth_open": 0.12, "asymmetry": 0.10},
    "sticker34.webp": {"smile": 0.18, "eye_open": 0.40},
    "sticker37.webp": {"eye_open": 0.48, "brow_raise": 0.28},
}


def get_reference_expression_profile(filename: str) -> dict[str, float]:
    preset_name = REFERENCE_EXPRESSION_PRESETS.get(filename, "neutral_poker")
    profile = dict(EXPRESSION_PRESETS[preset_name])

    for feature_name, value in REFERENCE_EXPRESSION_OVERRIDES.get(filename, {}).items():
        profile[feature_name] = value

    return profile
