import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Union

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

# 房间颜色循环
ROOM_COLORS = [
    (56, 189, 248),  # 蓝
    (52, 211, 153),  # 绿
    (167, 139, 250),  # 紫
    (251, 113, 133),  # 红
    (250, 204, 21),  # 黄
    (45, 212, 191),  # 青
    (251, 146, 60),  # 橙
]


def _extract_room_key(p: AnneOnlinePlayer) -> Tuple[str, str]:
    """提取房间标识 (完整服务器名, 模式)"""
    raw = p.get("server", "")
    if not raw or raw.strip() == "":
        return ("连接中...", p.get("mode", ""))
    return (raw.strip(), p.get("mode", ""))


async def draw_server_status_img(
    status: AnneStatus,
    players: List[AnneOnlinePlayer],
) -> Union[str, bytes]:
    img = _prepare_bg(900, 1800)
    draw = ImageDraw.Draw(img)
    w, _ = img.size

    # ── 顶部标题 ──
    for i in range(3):
        draw.rectangle(
            [(0, i * 40), (900, i * 40 + 40)],
            fill=(56, 189, 248, int(80 * (1 - i / 3))),
        )
    draw.text((40, 22), "Anne 电信服 · 服务器状态", font=l4_font_30, fill=Colors.TEXT_DARK + (240,))

    # ── 统计卡片 ──
    card_w, card_h, hgap, vgap = 210, 95, 50, 25
    cards_total = 3 * card_w + 2 * hgap
    cards_x = (w - cards_total) // 2
    for i, (label, key, color) in enumerate(STAT_CARDS):
        x = cards_x + (i % 3) * (card_w + hgap)
        y = 80 + (i // 3) * (card_h + vgap)
        draw_dark_stat_card(draw, (x, y), (card_w, card_h), label, str(status[key]), color)

    # ── 按房间分组 ──
    rooms: Dict[Tuple[str, str], List[AnneOnlinePlayer]] = defaultdict(list)
    for p in players:
        key = _extract_room_key(p)
        rooms[key].append(p)

    # 排序：连接中... 排最后，其余按房间名排序
    sorted_rooms = sorted(
        rooms.items(),
        key=lambda item: (
            1 if item[0][0] == "连接中..." else 0,
            item[0][0].lower(),
        ),
    )

    section_y = 80 + 2 * (card_h + vgap)
    draw.text(
        (MARGIN_X, section_y),
        f"当前在线玩家 ({status['online_now']} 人 / {len(rooms)} 个房间)",
        font=l4_font_26,
        fill=Colors.ACCENT_CYAN + (240,),
    )

    room_top = section_y + 40
    room_y = room_top
    room_color_idx = 0
    row_h = 26
    col_w = [20, 160, 90, 70]  # #, 玩家, 分数, 时间

    for (map_name, mode), members in sorted_rooms:
        accent = ROOM_COLORS[room_color_idx % len(ROOM_COLORS)]
        room_color_idx += 1

        # 房间标题栏（深色不透明底 + 彩色左边条 + 白色文字）
        mode_tag = f"[{mode}]" if mode else ""
        header_text = f"{map_name}  {mode_tag}  ({len(members)}人)"
        header_h = 32

        # 标题背景
        draw.rounded_rectangle(
            [MARGIN_X, room_y, w - MARGIN_X, room_y + header_h],
            radius=6,
            fill=(20, 28, 46, 255),
            outline=accent + (200,),
            width=1,
        )
        # 左侧彩色条
        draw.rounded_rectangle(
            [MARGIN_X + 2, room_y + 4, MARGIN_X + 6, room_y + header_h - 4],
            radius=2,
            fill=accent + (255,),
        )
        # 标题文字 — 白色
        draw.text(
            (MARGIN_X + 16, room_y + 4),
            header_text,
            font=l4_font_20,
            fill=(255, 255, 255, 255),
        )

        room_y += header_h

        # 玩家列表（实心深色交替行 + 白色文字）
        for pi, p in enumerate(members):
            ry = room_y + pi * row_h
            # 交替行背景：深色/更深色 交替，不透明
            if pi % 2 == 0:
                row_bg = (17, 24, 39, 255)
            else:
                row_bg = (13, 18, 30, 255)
            draw.rectangle(
                [MARGIN_X, ry, w - MARGIN_X, ry + row_h],
                fill=row_bg,
            )

            # 排名 — 浅灰色
            draw.text(
                (MARGIN_X + col_w[0] // 2 - 8, ry + 3),
                p["rank"],
                font=l4_font_16,
                fill=(200, 200, 200, 255),
            )
            # 玩家名 — 白色
            name_text = p["name"][:16]
            draw.text(
                (MARGIN_X + col_w[0] + 4, ry + 3),
                name_text,
                font=l4_font_16,
                fill=(255, 255, 255, 255),
            )
            # 积分 — 房间主题色 (x右移150px)
            draw.text(
                (MARGIN_X + col_w[0] + col_w[1] + 4 + 200, ry + 3),
                p["score"],
                font=l4_font_16,
                fill=accent + (255,),
            )
            # 游玩时间 — 浅灰 (左移20px)
            draw.text(
                (MARGIN_X + col_w[0] + col_w[1] + col_w[2] + 4 - 20, ry + 3),
                p["playtime"],
                font=l4_font_16,
                fill=(180, 180, 180, 255),
            )

        room_y += len(members) * row_h + 12

        # 如果超出底部就截断
        if room_y > 1100:
            break

    # ── 底部 ──
    footer_y = max(room_y + 20, section_y + 60)
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
