"""聊天记录图片渲染 —— Discord 风格"""

from pathlib import Path
from typing import Dict, List, Union

from gsuid_core.utils.image.convert import convert_img
from PIL import Image, ImageDraw

from ..l4_info.pil_utils import Colors, prepare_bg
from ..utils.l4_font import l4_font_16, l4_font_20, l4_font_30

TEXTURED = Path(__file__).parent.parent / "l4_info" / "texture2d" / "anne"
MARGIN_X = 40

COLORS_CYCLE = [
    (56, 189, 248),
    (52, 211, 153),
    (167, 139, 250),
    (251, 113, 133),
    (250, 204, 21),
    (45, 212, 191),
    (251, 146, 60),
]


def _prepare_bg(w: int = 900, h: int = 1200) -> Image.Image:
    return prepare_bg(TEXTURED / "bg", w, h)


def _draw_header(draw: ImageDraw.ImageDraw, title: str, w: int = 900):
    for i in range(3):
        draw.rectangle(
            [(0, i * 40), (w, i * 40 + 40)],
            fill=(56, 189, 248, int(80 * (1 - i / 3))),
        )
    draw.text((40, 22), title, font=l4_font_30, fill=Colors.TEXT_DARK + (240,))


def _draw_footer(draw: ImageDraw.ImageDraw, y: int, w: int = 900):
    draw.rounded_rectangle(
        [MARGIN_X, y, w - MARGIN_X, y + 40],
        radius=8,
        fill=Colors.PROFESSIONAL_BG + (200,),
        outline=Colors.PROFESSIONAL_BORDER + (80,),
        width=1,
    )
    draw.text(
        (MARGIN_X + 15, y + 10),
        "数据来源: anne.trygek.com/chat/",
        font=l4_font_20,
        fill=Colors.TEXT_LIGHT_GRAY + (150,),
    )


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


async def draw_chat_messages(
    groups: Dict[str, List],
    server_name: str = "",
) -> Union[str, bytes]:
    """绘制聊天记录 —— Discord 风格

    Args:
        groups: { 服务器名: [ChatMessage, ...] }
        server_name: 标题后缀
    """
    if not groups:
        return "暂无聊天记录"

    total = sum(len(v) for v in groups.values())
    w = 900
    msg_h = 44  # 每条消息高度
    grp_h = 32  # 服务器标题栏高度
    est = 120 + len(groups) * grp_h + total * msg_h + 100
    img = _prepare_bg(w, max(600, est))
    draw = ImageDraw.Draw(img)

    title = "Anne 聊天记录"
    if server_name:
        title += f" · {server_name}"
    _draw_header(draw, title, w)

    y = 90
    draw.text(
        (MARGIN_X, y),
        f"共 {total} 条 · {len(groups)} 个服务器",
        font=l4_font_20,
        fill=Colors.ACCENT_CYAN + (240,),
    )
    y += 32

    color_idx = 0

    for srv_name, msgs in groups.items():
        accent = COLORS_CYCLE[color_idx % len(COLORS_CYCLE)]
        color_idx += 1

        # ── 服务器标题 ──
        short_name = srv_name
        if "[" in srv_name:
            short_name = srv_name[: srv_name.index("[")].strip()
        draw.rounded_rectangle(
            [MARGIN_X, y, w - MARGIN_X, y + grp_h],
            radius=6,
            fill=accent + (25,),
            outline=accent + (120,),
            width=1,
        )
        draw.rounded_rectangle(
            [MARGIN_X + 2, y + 4, MARGIN_X + 5, y + grp_h - 4],
            radius=2,
            fill=accent + (255,),
        )
        draw.text(
            (MARGIN_X + 14, y + 5),
            f"{short_name}  ({len(msgs)} 条)",
            font=l4_font_20,
            fill=(255, 255, 255, 255),
        )
        y += grp_h + 2

        # ── 消息列表（时间正序：旧→新，同角色合并）
        msgs = list(reversed(msgs))
        prev_player = ""
        for mi, msg in enumerate(msgs):
            my = y + mi * msg_h
            player = msg.get("player", "")
            is_same = player == prev_player and player != ""
            prev_player = player

            # 左侧时间 + 类型指示器（仅非合并消息显示）
            if not is_same:
                t = msg.get("time", "")
                time_str = t[11:16] if len(t) > 16 else t
                draw.text(
                    (MARGIN_X + 4, my + 2),
                    time_str,
                    font=l4_font_16,
                    fill=Colors.TEXT_LIGHT_GRAY + (130,),
                )

                # 类型彩色小点
                msg_type = msg.get("msg_type", "")
                dot_color = (56, 189, 248, 220) if "团队" in msg_type else (148, 163, 184, 160)
                draw.ellipse(
                    [MARGIN_X + 62, my + 6, MARGIN_X + 72, my + 16],
                    fill=dot_color,
                )

                # 玩家名
                draw.text(
                    (MARGIN_X + 80, my + 1),
                    _truncate(player, 14),
                    font=l4_font_20,
                    fill=accent + (240,),
                )

                # 消息内容（首条位置偏下）
                content = msg.get("content", "")
                draw.text(
                    (MARGIN_X + 80, my + 22),
                    _truncate(content, 55),
                    font=l4_font_16,
                    fill=Colors.TEXT_LIGHT_GRAY + (200,),
                )
            else:
                # 合并消息：左侧灰色竖线 + 内容
                draw.line(
                    [(MARGIN_X + 66, my), (MARGIN_X + 66, my + msg_h - 4)],
                    fill=(255, 255, 255, 25),
                    width=2,
                )
                content = msg.get("content", "")
                draw.text(
                    (MARGIN_X + 80, my + 6),
                    _truncate(content, 55),
                    font=l4_font_16,
                    fill=Colors.TEXT_LIGHT_GRAY + (200,),
                )

            # 地图名（灰字，右上角）
            map_name = msg.get("map_name", "")
            if map_name:
                mt = _truncate(map_name, 14)
                draw.text(
                    (w - MARGIN_X - 4, my + 2),
                    mt,
                    font=l4_font_16,
                    fill=Colors.TEXT_LIGHT_GRAY + (100,),
                    anchor="rt",
                )

            # 消息间分割线（合并消息省略）
            if not is_same and mi < len(msgs) - 1:
                next_same = mi + 1 < len(msgs) and msgs[mi + 1].get("player", "") == player
                if not next_same:
                    draw.line(
                        [(MARGIN_X + 14, my + msg_h - 1), (w - MARGIN_X - 14, my + msg_h - 1)],
                        fill=(255, 255, 255, 12),
                        width=1,
                    )

        y += len(msgs) * msg_h + 6

        if y > 1100:
            break

    footer_y = max(y + 10, 700)
    _draw_footer(draw, footer_y, w)
    crop_h = min(footer_y + 70, img.size[1])
    img = img.crop((0, 0, w, crop_h))
    return await convert_img(img)
