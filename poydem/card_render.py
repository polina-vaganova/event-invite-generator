"""
Сборка финальной открытки через Pillow.

Складывает в одну картинку:
  • короткую фразу (текст от ИИ) — сверху;
  • персонажа (прозрачный PNG от нейросети) — по центру;
  • название / дату / место события — снизу.

Возвращает байты PNG.
"""
import ast
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path(__file__).parent / "static" / "fonts" / "Montserrat.ttf"

W, H = 1024, 1280
MARGIN = 70
DARK = (30, 25, 40)         # основной тёмный текст
MUTED = (90, 80, 95)        # приглушённый текст (дата/место)

# Палитра пастельных фонов (выбор пользователя после генерации)
PALETTE = {
    "pink":     (247, 231, 240),
    "lavender": (235, 230, 248),
    "mint":     (223, 242, 232),
    "peach":    (251, 233, 218),
    "sky":      (224, 237, 250),
    "lemon":    (246, 242, 208),
}
DEFAULT_BG = "pink"


def _font(size: int, weight: int = 700) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONT_PATH), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:  # noqa: BLE001 — если веса недоступны, берём как есть
        pass
    return f


def _mix(c, other, t: float) -> tuple:
    """Смешивает цвет c с other на долю t (0..1)."""
    return tuple(int(c[i] + (other[i] - c[i]) * t) for i in range(3))


def _gradient_bg(color: tuple) -> Image.Image:
    """Мягкий вертикальный градиент-перелив: светлее сверху, чуть глубже снизу."""
    top = _mix(color, (255, 255, 255), 0.28)      # светлее
    bottom = _mix(color, (40, 30, 55), 0.10)       # чуть насыщеннее/глубже
    base = Image.new("RGB", (W, H), top)
    deep = Image.new("RGB", (W, H), bottom)
    mask = Image.linear_gradient("L").resize((W, H))  # 0 сверху → 255 снизу
    return Image.composite(deep, base, mask)


def _as_list(value) -> list[str]:
    """Жанры могут лежать строкой-репром списка — приводим к списку строк."""
    if isinstance(value, (list, tuple)):
        return [str(x) for x in value]
    if isinstance(value, str) and value.strip().startswith("["):
        try:
            return [str(x) for x in ast.literal_eval(value)]
        except Exception:  # noqa: BLE001
            pass
    return [value] if value else []


def _meta_lines(event: dict) -> list[str]:
    """До двух строк под названием: дата/место (события) или жанры/длительность (кино)."""
    if event.get("date") or event.get("venue"):
        return [v for v in [event.get("date"), event.get("venue")] if v][:2]
    lines = []
    genres = _as_list(event.get("genres"))
    if genres:
        lines.append("  ·  ".join(genres))
    tail = "  ·  ".join(str(v) for v in [event.get("duration"), event.get("price")] if v)
    if tail:
        lines.append(tail)
    return lines[:2]


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    """Перенос текста по словам, чтобы влезал по ширине."""
    lines, cur = [], ""
    for word in text.split():
        test = (cur + " " + word).strip()
        if draw.textlength(test, font=font) <= max_width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def render_card(event: dict, text: str, character_png: bytes, bg: str = DEFAULT_BG) -> bytes:
    """Собирает открытку: фраза + персонаж + инфо события → PNG."""
    color = PALETTE.get(bg, PALETTE[DEFAULT_BG])
    canvas = _gradient_bg(color).convert("RGBA")  # фон с мягким переливом
    draw = ImageDraw.Draw(canvas)

    # --- Фраза сверху ---
    phrase_font = _font(60, 800)
    lines = _wrap(draw, text, phrase_font, W - 2 * MARGIN)
    y = 80
    for line in lines:
        lw = draw.textlength(line, font=phrase_font)
        draw.text(((W - lw) / 2, y), line, font=phrase_font, fill=DARK)
        y += int(phrase_font.size * 1.15)

    # --- Персонаж по центру ---
    info_block_h = 240
    top = y + 30
    avail_h = H - top - info_block_h - 40
    avail_w = W - 2 * MARGIN
    char = Image.open(io.BytesIO(character_png)).convert("RGBA")
    scale = min(avail_w / char.width, avail_h / char.height)
    new_w, new_h = max(1, int(char.width * scale)), max(1, int(char.height * scale))
    char = char.resize((new_w, new_h), Image.LANCZOS)
    cx = (W - new_w) // 2
    cy = top + (avail_h - new_h) // 2
    canvas.alpha_composite(char, (cx, max(top, cy)))

    # --- Инфо события снизу ---
    iy = H - info_block_h
    draw.line([(MARGIN, iy), (W - MARGIN, iy)], fill=(0, 0, 0, 35), width=2)
    title_font = _font(44, 800)
    info_font = _font(30, 500)

    ty = iy + 26
    for line in _wrap(draw, event.get("title", ""), title_font, W - 2 * MARGIN)[:1]:
        draw.text((MARGIN, ty), line, font=title_font, fill=DARK)
        ty += int(title_font.size * 1.05)

    # Доп. инфо — отдельными строками, каждая обрезается по ширине
    ty += 6
    for value in _meta_lines(event):
        line = value
        while draw.textlength(line, font=info_font) > W - 2 * MARGIN and len(line) > 4:
            line = line[:-2]
        if line != value:
            line = line.rstrip(" ,«") + "…"
        draw.text((MARGIN, ty), line, font=info_font, fill=MUTED)
        ty += int(info_font.size * 1.25)

    out = io.BytesIO()
    canvas.convert("RGB").save(out, "PNG")
    return out.getvalue()
