import random
from pathlib import Path
from typing import List, Union

from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import draw_pic_with_ring, easy_paste
from PIL import Image, ImageDraw

from ..utils.api.models import AnneOnlinePlayer, AnneStatus
from ..utils.l4_font import l4_font_20, l4_font_22, l4_font_24, l4_font_26, l4_font_30, l4_font_36
from .panel_redesign import MARGIN_X, draw_dark_stat_card
from .pil_utils import Colors, load_image

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
    col_x = [MARGIN_X, 85, 290, 415, 600, 725]
    headers = ["#", "玩家", "模式", "服务器", "积分", "游玩时间"]
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
        mode = p["mode"]
        if len(mode) > 6:
            mode = mode[:4] + mode[-2:]
        server = p["server"]
        if "#" in server:
            server = server[server.index("#") :]
        else:
            server = ""
        draw.text((col_x[0], ry), p["rank"], font=l4_font_20, fill=Colors.TEXT_LIGHT_GRAY + (200,))
        draw.text((col_x[1], ry), p["name"], font=l4_font_20, fill=Colors.ACCENT_CYAN + (240,))
        draw.text((col_x[2], ry), mode, font=l4_font_20, fill=Colors.TEXT_LIGHT_GRAY + (180,))
        draw.text((col_x[3], ry), server[:20], font=l4_font_20, fill=Colors.TEXT_LIGHT_GRAY + (180,))
        draw.text((col_x[4], ry), p["score"], font=l4_font_20, fill=Colors.ACCENT_CYAN + (240,))
        draw.text((col_x[5], ry), p["playtime"], font=l4_font_20, fill=Colors.TEXT_LIGHT_GRAY + (200,))

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
