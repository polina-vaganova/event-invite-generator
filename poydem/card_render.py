"""
Сборка финальной открытки через Pillow.

Складывает в одну картинку:
  • короткую фразу (текст от ИИ) — сверху;
  • персонажа (прозрачный PNG от нейросети) — по центру;
  • название / дату / место события — снизу.

Возвращает байты PNG.
"""
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path(__file__).parent / "static" / "fonts" / "Montserrat.ttf"

W, H = 1024, 1280
MARGIN = 70
BG = (247, 231, 240)        # нежно-розовый пастельный фон
DARK = (30, 25, 40)         # основной тёмный текст
MUTED = (110, 95, 120)      # приглушённый текст (дата/место)


def _font(size: int, weight: int = 700) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONT_PATH), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:  # noqa: BLE001 — если веса недоступны, берём как есть
        pass
    return f


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


def render_card(event: dict, text: str, character_png: bytes) -> bytes:
    """Собирает открытку: фраза + персонаж + инфо события → PNG."""
    canvas = Image.new("RGBA", (W, H), BG + (255,))
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

    # Дата и место — отдельными строками, каждая обрезается по ширине
    ty += 6
    for value in [event.get("date"), event.get("venue")]:
        if not value:
            continue
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
