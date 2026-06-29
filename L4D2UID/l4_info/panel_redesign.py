from typing import Dict, List, Tuple

from PIL import Image, ImageDraw

from ..utils.l4_font import (
    l4_font_20,
    l4_font_24,
    l4_font_26,
    l4_font_28,
    l4_font_32,
)
from .pil_utils import Colors

MARGIN_X = 40


def draw_dark_stat_card(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int],
    size: Tuple[int, int],
    label: str,
    value: str,
    accent_color: Tuple[int, int, int],
) -> None:
    x, y = xy
    w, h = size

    draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=10,
        fill=Colors.PROFESSIONAL_BG + (230,),
        outline=Colors.PROFESSIONAL_BORDER + (120,),
        width=1,
    )

    draw.rounded_rectangle(
        [x + 12, y, x + w - 12, y + 3],
        radius=2,
        fill=accent_color + (200,),
    )

    value_text = str(value)
    if len(value_text) > 9:
        vfont = l4_font_24
    elif len(value_text) > 7:
        vfont = l4_font_28
    else:
        vfont = l4_font_32

    vbox = draw.textbbox((0, 0), value_text, font=vfont)
    vw = vbox[2] - vbox[0]
    draw.text(
        (x + (w - vw) // 2, y + 18),
        value_text,
        font=vfont,
        fill=accent_color + (240,),
    )

    lbox = draw.textbbox((0, 0), label, font=l4_font_20)
    lw = lbox[2] - lbox[0]
    draw.text(
        (x + (w - lw) // 2, y + h - 28),
        label,
        font=l4_font_20,
        fill=Colors.TEXT_LIGHT_GRAY + (200,),
    )


def draw_data_panel(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int],
    size: Tuple[int, int],
    title: str,
    data_dict: Dict[str, str],
    title_color: Tuple[int, int, int] = Colors.ACCENT_CYAN,
    data_rows: int = 5,
) -> None:
    x, y = xy
    w, h = size

    draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=12,
        fill=Colors.PROFESSIONAL_BG + (220,),
        outline=Colors.PROFESSIONAL_BORDER + (100,),
        width=1,
    )

    title_y = y + 14
    draw.text((x + 20, title_y), title, font=l4_font_26, fill=Colors.TEXT_DARK + (240,))

    tbox = draw.textbbox((0, 0), title, font=l4_font_26)
    tw = tbox[2] - tbox[0]
    draw.line(
        [(x + 20, title_y + 30), (x + 20 + tw + 40, title_y + 30)],
        fill=title_color + (150,),
        width=2,
    )

    row_start = y + 52
    row_h = (h - 52 - 14) // data_rows

    items = list(data_dict.items())
    for i, (label, value) in enumerate(items):
        ry = row_start + i * row_h

        draw.text((x + 20, ry + 3), label, font=l4_font_20, fill=Colors.TEXT_LIGHT_GRAY + (200,))

        value_text = str(value)
        vbox = draw.textbbox((0, 0), value_text, font=l4_font_24)
        vw = vbox[2] - vbox[0]
        draw.text(
            (x + w - vw - 20, ry + 2),
            value_text,
            font=l4_font_24,
            fill=title_color + (240,),
        )

        if i < len(items) - 1:
            draw.line(
                [(x + 20, ry + row_h - 1), (x + w - 20, ry + row_h - 1)],
                fill=Colors.PROFESSIONAL_BORDER + (60,),
                width=1,
            )


STAT_CARD_CONFIGS: List[Tuple[str, str, Tuple[int, int, int]]] = [
    ("总积分", "source", Colors.ACCENT_CYAN),
    ("总击杀", "kills", Colors.ACCENT_GREEN),
    ("爆头率", "avg_headshots", Colors.ACCENT_YELLOW),
    ("PPM", "ppm", Colors.ACCENT_RED),
]

QUARTER_STAT_CARD_CONFIGS: List[Tuple[str, str, Tuple[int, int, int]]] = [
    ("季度积分", "source", Colors.ACCENT_CYAN),
    ("季度击杀", "kills", Colors.ACCENT_GREEN),
    ("爆头率", "avg_headshots", Colors.ACCENT_YELLOW),
    ("季度PPM", "ppm", Colors.ACCENT_RED),
]

QUARTER_PANEL_CONFIGS: List[Dict] = [
    {
        "title": "季度辅助数据",
        "color": Colors.ACCENT_GREEN,
        "keys": [
            ("近战击杀", "melee_charge"),
            ("地图通关", "map_clear"),
            ("给药次数", "pills_give"),
            ("扶起倒地", "friend_up"),
            ("保护队友(普感)", "protect_friend"),
        ],
    },
    {
        "title": "季度扣分行为",
        "color": Colors.ACCENT_RED,
        "keys": [
            ("黑枪次数", "mistake_shout"),
            ("杀死队友", "kill_friend"),
            ("击倒队友", "down_friend"),
            ("放弃队友", "abandon_friend"),
            ("让感染入安全门", "put_into"),
            ("惊扰Witch", "agitate_witch"),
        ],
    },
]

PANEL_CONFIGS: List[Dict] = [
    {
        "title": "辅助数据",
        "color": Colors.ACCENT_GREEN,
        "keys": [
            ("近战击杀", "melee_charge"),
            ("地图通关", "map_clear"),
            ("给药次数", "pills_give"),
            ("扶起倒地", "friend_up"),
            ("保护队友(普感)", "protect_friend"),
        ],
    },
    {
        "title": "扣分行为",
        "color": Colors.ACCENT_RED,
        "keys": [
            ("黑枪次数", "mistake_shout"),
            ("杀死队友", "kill_friend"),
            ("击倒队友", "down_friend"),
            ("放弃队友", "abandon_friend"),
            ("让感染入安全门", "put_into"),
            ("惊扰Witch", "agitate_witch"),
        ],
    },
]


def create_professional_player_stats(
    bg_img: Image.Image,
    player_data: dict,
    top_offset: int = 0,
    stat_card_configs: list[tuple[str, str, tuple[int, int, int]]] | None = None,
    panel_configs: list[dict] | None = None,
    draw_footer: bool = True,
) -> tuple[Image.Image, int]:
    _sc_configs = stat_card_configs or STAT_CARD_CONFIGS
    _p_configs = panel_configs or PANEL_CONFIGS

    img = bg_img.copy().convert("RGBA")
    draw = ImageDraw.Draw(img)

    img_w, img_h = img.size

    card_w = 175
    card_h = 95
    card_gap = 20
    cards_total = len(_sc_configs) * card_w + (len(_sc_configs) - 1) * card_gap
    cards_x = (img_w - cards_total) // 2
    cards_y = top_offset + 10

    for i, (label, key, color) in enumerate(_sc_configs):
        x = cards_x + i * (card_w + card_gap)
        value = str(player_data.get(key, "0"))
        if key == "avg_headshots" and value.endswith("%"):
            value = value
        draw_dark_stat_card(draw, (x, cards_y), (card_w, card_h), label, value, color)

    panels_top = cards_y + card_h + 40
    panel_w = 390
    panel_h = 270
    panel_gap = 25

    left_x = MARGIN_X
    right_x = img_w - MARGIN_X - panel_w

    for idx, cfg in enumerate(_p_configs):
        col = idx % 2
        row = idx // 2
        x = left_x if col == 0 else right_x
        y = panels_top + row * (panel_h + panel_gap)

        data_dict = {}
        for label, key in cfg["keys"]:
            data_dict[label] = str(player_data.get(key, "0"))

        draw_data_panel(
            draw,
            (x, y),
            (panel_w, panel_h),
            cfg["title"],
            data_dict,
            cfg["color"],
            data_rows=len(cfg["keys"]),
        )

    num_rows = (len(_p_configs) + 1) // 2
    section_end = panels_top + num_rows * (panel_h + panel_gap)

    if draw_footer:
        footer_y = panels_top + num_rows * (panel_h + panel_gap) + 20
        draw.rounded_rectangle(
            [MARGIN_X, footer_y, img_w - MARGIN_X, footer_y + 40],
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
        section_end = footer_y + 40

    return img, section_end
