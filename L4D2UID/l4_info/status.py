import random
from pathlib import Path
from typing import Dict, List, Union

from gsuid_core.utils.image.convert import convert_img
from PIL import Image, ImageDraw

from ..utils.api.models import AnneAward, AnneOnlinePlayer, AnneStatus
from ..utils.l4_font import l4_font_16, l4_font_20, l4_font_22, l4_font_24, l4_font_26, l4_font_30
from .panel_redesign import MARGIN_X, draw_dark_stat_card
from .pil_utils import Colors

TEXTURED = Path(__file__).parent / "texture2d" / "anne"


def _prepare_bg(w: int = 900, h: int = 1200) -> Image.Image:
    bg = list((TEXTURED / "bg").glob("*.png"))
    img = Image.open(random.choice(bg))
    img = img.resize((w, h)) if img.size != (w, h) else img
    overlay = Image.new("RGBA", img.size, (10, 14, 23, 210))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


STAT_CARDS = [
    ("总玩家数", "total_players", Colors.ACCENT_CYAN),
    ("总击杀数", "total_kills", Colors.ACCENT_RED),
    ("总爆头数", "total_headshots", Colors.ACCENT_YELLOW),
    ("当前在线", "online_now", Colors.ACCENT_GREEN),
    ("今日在线过", "today_online", Colors.ACCENT_TEAL),
    ("30天活跃", "active_30d", Colors.ACCENT_PURPLE),
]


async def draw_server_status_img(
    status: AnneStatus,
    players: List[AnneOnlinePlayer],
) -> Union[str, bytes]:
    img = _prepare_bg(900, 1200)
    draw = ImageDraw.Draw(img)
    w, _ = img.size

    for i in range(3):
        draw.rectangle([(0, i * 40), (900, i * 40 + 40)], fill=(56, 189, 248, int(80 * (1 - i / 3))))
    draw.text((40, 22), "Anne 电信服 · 服务器状态", font=l4_font_30, fill=Colors.TEXT_DARK + (240,))

    card_w, card_h, hgap, vgap = 210, 95, 50, 25
    cards_total = 3 * card_w + 2 * hgap
    cards_x = (w - cards_total) // 2
    for i, (label, key, color) in enumerate(STAT_CARDS):
        x = cards_x + (i % 3) * (card_w + hgap)
        y = 80 + (i // 3) * (card_h + vgap)
        draw_dark_stat_card(draw, (x, y), (card_w, card_h), label, str(status[key]), color)

    section_y = 80 + 2 * (card_h + vgap)
    draw.text(
        (MARGIN_X, section_y),
        f"当前在线玩家  ({status['online_now']} 人)",
        font=l4_font_26,
        fill=Colors.ACCENT_CYAN + (240,),
    )

    table_top = section_y + 40
    col_x = [MARGIN_X, 85, 360, 720]
    headers = ["#", "玩家", "服务器", "积分"]
    draw.rounded_rectangle(
        [MARGIN_X - 5, table_top - 8, w - MARGIN_X + 5, table_top + 30],
        radius=6,
        fill=(17, 24, 39, 220),
        outline=(55, 65, 81, 150),
        width=1,
    )
    for j, hdr in enumerate(headers):
        draw.text((col_x[j], table_top), hdr, font=l4_font_20, fill=Colors.TEXT_LIGHT_GRAY + (200,))

    row_h = 32
    for i, p in enumerate(players[:30]):
        ry = table_top + 38 + i * row_h
        if i % 2 == 0:
            draw.rectangle(
                [MARGIN_X - 5, ry - 4, w - MARGIN_X + 5, ry + row_h - 4],
                fill=(255, 255, 255, 8),
            )
        server = p["server"]
        if "#" in server:
            server = server[server.index("#") :]
        else:
            server = ""
        draw.text((col_x[0], ry), p["rank"], font=l4_font_20, fill=Colors.TEXT_LIGHT_GRAY + (200,))
        draw.text((col_x[1], ry), p["name"], font=l4_font_20, fill=Colors.ACCENT_CYAN + (240,))
        draw.text((col_x[2], ry), server[:30], font=l4_font_20, fill=Colors.TEXT_LIGHT_GRAY + (180,))
        draw.text((col_x[3], ry), p["score"], font=l4_font_20, fill=Colors.ACCENT_CYAN + (240,))

    footer_y = table_top + 38 + min(len(players), 30) * row_h + 25
    draw.rounded_rectangle(
        [MARGIN_X, footer_y, w - MARGIN_X, footer_y + 40],
        radius=8,
        fill=Colors.PROFESSIONAL_BG + (200,),
        outline=Colors.PROFESSIONAL_BORDER + (80,),
        width=1,
    )
    draw.text(
        (MARGIN_X + 15, footer_y + 10),
        "数据来源: anne.trygek.com",
        font=l4_font_20,
        fill=Colors.TEXT_LIGHT_GRAY + (150,),
    )

    crop_h = min(footer_y + 80, img.size[1])
    img = img.crop((0, 0, img.size[0], crop_h))
    return await convert_img(img)


async def draw_awards_img(awards: List[AnneAward]) -> Union[str, bytes]:
    img = _prepare_bg(900, 1800)
    draw = ImageDraw.Draw(img)
    w, _ = img.size

    for i in range(3):
        draw.rectangle([(0, i * 40), (900, i * 40 + 40)], fill=(56, 189, 248, int(80 * (1 - i / 3))))
    draw.text((40, 22), "Anne 电信服 · 服务器荣誉殿堂", font=l4_font_30, fill=Colors.TEXT_DARK + (240,))

    y = 140
    categories: Dict[str, List[AnneAward]] = {}
    for a in awards:
        categories.setdefault(a["category"], []).append(a)

    cw, ch, cgap = 265, 123, 12
    for cat, items in categories.items():
        draw.text((MARGIN_X, y), cat, font=l4_font_24, fill=Colors.ACCENT_CYAN + (240,))
        y += 32
        for idx, a in enumerate(items):
            if y > 1720:
                break
            col = idx % 3
            row = idx // 3
            cx = MARGIN_X + col * (cw + cgap)
            cy = y + row * (ch + cgap)
            draw.rounded_rectangle(
                [cx, cy, cx + cw, cy + ch],
                radius=8,
                fill=Colors.PROFESSIONAL_BG + (220,),
                outline=Colors.PROFESSIONAL_BORDER + (100,),
                width=1,
            )
            draw.text((cx + 10, cy + 8), a["title"], font=l4_font_22, fill=Colors.ACCENT_CYAN + (240,))
            desc = a["desc"]
            d1 = desc[:14]
            d2 = desc[14:28]
            draw.text((cx + 10, cy + 32), d1, font=l4_font_16, fill=Colors.TEXT_LIGHT_GRAY + (180,))
            draw.text((cx + 10, cy + 50), d2, font=l4_font_16, fill=Colors.TEXT_LIGHT_GRAY + (180,))
            draw.text((cx + 10, cy + 70), a["winner"], font=l4_font_20, fill=Colors.TEXT_DARK + (240,))
            draw.text((cx + 10, cy + 94), f"成绩: {a['score']}", font=l4_font_20, fill=Colors.TEXT_LIGHT_GRAY + (200,))
        y += ((len(items) + 2) // 3) * (ch + cgap) + 15

    footer_y = y + 10
    draw.rounded_rectangle(
        [MARGIN_X, footer_y, w - MARGIN_X, footer_y + 40],
        radius=8,
        fill=Colors.PROFESSIONAL_BG + (200,),
        outline=Colors.PROFESSIONAL_BORDER + (80,),
        width=1,
    )
    draw.text(
        (MARGIN_X + 15, footer_y + 10),
        "数据来源: anne.trygek.com",
        font=l4_font_20,
        fill=Colors.TEXT_LIGHT_GRAY + (150,),
    )

    crop_h = min(footer_y + 80, img.size[1])
    img = img.crop((0, 0, img.size[0], crop_h))
    return await convert_img(img)
