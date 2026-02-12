from typing import Dict, Tuple

from PIL import Image, ImageDraw

from .pil_utils import Colors, draw_stat_card, draw_professional_panel
from ..utils.l4_font import l4_font_20, l4_font_24, l4_font_26, l4_font_30, l4_font_32, l4_font_36, l4_font_40

# 间距和尺寸
MARGIN_RATIO = 0.05
GAP_MIN = 25
GAP_RATIO = 0.04

# 顶部统计卡片
STAT_CARD_MAX_WIDTH = 220
STAT_CARD_HEIGHT_RATIO = 0.14
STAT_CARD_TOP_OFFSET = 50

# 数据面板
PANEL_GAP_BETWEEN_STAT = 80
PANEL_MAX_HEIGHT = 350
PANEL_MIN_HEIGHT = 220
PANEL_MAX_WIDTH = 420
PANEL_HEIGHT_RATIO = 0.02

# 最小化面板
MIN_PANEL_WIDTH = 900
MIN_PANEL_HEIGHT = 150
MIN_PANEL_PADDING = 20

# 面板配置
PANEL_CONFIGS = [
    {
        "title": "基础信息",
        "title_font": l4_font_30,
        "data_keys": [("分数", "source"), ("击杀", "kills"), ("排名", "rank"), ("游戏时长", "playtime")],
        "value_color": Colors.ACCENT_BLUE,
        "format_rank": True,  # 排名需要添加#前缀
    },
    {
        "title": "黑枪数据",
        "title_font": l4_font_26,
        "data_keys": [
            ("黑枪次数", "mistake_shout"),
            ("杀死队友", "kill_friend"),
            ("击倒队友", "down_friend"),
            ("放弃队友", "abandon_friend"),
        ],
        "value_color": Colors.ACCENT_RED,
    },
    {
        "title": "队友协作",
        "title_font": l4_font_26,
        "data_keys": [
            ("药丸赠与", "pills_give"),
            ("救援队友", "protect_friend"),
            ("秒妹数量", "witch_instantly_kill"),
            ("地图完成", "map_clear"),
        ],
        "value_color": Colors.ACCENT_GREEN,
    },
    {
        "title": "其他数据",
        "title_font": l4_font_26,
        "data_keys": [("占位符1", "zw1"), ("占位符2", "zw2"), ("占位符3", "zw3"), ("占位符4", "zw4")],
        "value_color": Colors.ACCENT_YELLOW,
    },
]


def _build_data_dict(config: Dict, player_data: Dict) -> Dict[str, str]:
    """
    根据配置和玩家数据构建面板数据字典

    Args:
        config: 面板配置（包含data_keys）
        player_data: 玩家数据

    Returns:
        标签-值映射字典
    """
    data_dict = {}
    for label, key in config["data_keys"]:
        value = player_data.get(key, "--")
        # 排名数据需要特殊处理
        if config.get("format_rank") and key == "rank":
            value = f"#{value}"
        data_dict[label] = str(value)
    return data_dict


def _build_stat_card_config(accent_color: Tuple[int, int, int]) -> Dict:
    """
    为统计卡片生成通用配置字典

    Args:
        accent_color: 强调色

    Returns:
        卡片配置字典
    """
    return {
        "stat_font": l4_font_36,
        "label_font": l4_font_32,
        "label_color": Colors.TEXT_LIGHT_GRAY,
        "value_color": accent_color,
        "bg_color": Colors.PROFESSIONAL_CARD + (245,),
        "border_color": accent_color + (180,),
    }


def _build_panel_config() -> Dict:
    """
    为数据面板生成通用配置字典

    Returns:
        面板配置字典
    """
    return {
        "label_font": l4_font_20,
        "value_font": l4_font_24,
        "title_color": Colors.PROFESSIONAL_TITLE,
        "label_color": Colors.TEXT_LIGHT_GRAY,
        "bg_color": Colors.PROFESSIONAL_CARD + (245,),
        "border_color": Colors.PROFESSIONAL_BORDER + (160,),
    }


def create_professional_player_stats(
    bg_img: Image.Image,
    player_data: dict,
    top_offset: int = 0,
) -> Image.Image:
    """
    创建专业玩家统计面板

    Args:
        bg_img: 背景图片
        player_data: 玩家数据字典
        top_offset: 预留的顶部高度（用于标题/头像）

    Returns:
        包含面板的图片对象
    """
    img = bg_img.copy().convert("RGBA")
    draw = ImageDraw.Draw(img)

    img_width, img_height = img.size

    margin_x = int(img_width * MARGIN_RATIO)
    margin_y = max(top_offset + int(img_height * PANEL_HEIGHT_RATIO), int(img_height * 0.04))
    gap = max(GAP_MIN, int(img_width * GAP_RATIO))

    # 顶部卡片
    card_w = min(STAT_CARD_MAX_WIDTH, int((img_width - 2 * margin_x - 3 * gap) / 4))
    card_h = min(140, int(img_height * STAT_CARD_HEIGHT_RATIO))
    total_stat_w = 4 * card_w + 3 * gap
    stat_start_x = (img_width - total_stat_w) // 2
    stat_y = margin_y + STAT_CARD_TOP_OFFSET

    stat_items = [
        ("分数", str(player_data.get("source", 0)), Colors.ACCENT_BLUE),
        ("排名", str(player_data.get("rank", 0)), Colors.ACCENT_GREEN),
        ("爆头率", str(player_data.get("avg_headshots", "0%")), Colors.ACCENT_YELLOW),
        ("PPM", str(player_data.get("ppm", "--")), Colors.ACCENT_RED),
    ]

    _ = _build_stat_card_config(Colors.ACCENT_BLUE)
    for i, (label, value, color) in enumerate(stat_items):
        x = stat_start_x + i * (card_w + gap)
        config = _build_stat_card_config(color)
        if label == "分数" and len(value) > 7:
            config["stat_font"] = l4_font_32
        draw_stat_card(
            draw,
            xy=(x, stat_y),
            size=(card_w, card_h),
            label=label,
            value=value.replace("%", "") if isinstance(value, str) else str(value),
            **config,
        )

    # 方格数据数值
    panels_area_top = stat_y + card_h + PANEL_GAP_BETWEEN_STAT
    panels_area_h = img_height - panels_area_top - margin_y

    max_panel_h = (panels_area_h - gap) // 2
    panel_h = min(PANEL_MAX_HEIGHT, max(PANEL_MIN_HEIGHT, max_panel_h))
    panel_w = min(PANEL_MAX_WIDTH, (img_width - 3 * margin_x) // 2)

    used_h = panel_h * 2 + gap
    panels_area_y = panels_area_top + max(0, (panels_area_h - used_h) // 2)

    left_x = margin_x
    right_x = img_width - margin_x - panel_w

    # 面板公共配置
    panel_base_config = _build_panel_config()

    # 绘制方格数据（1/2）
    for panel_idx, config in enumerate(PANEL_CONFIGS[:2]):
        x = left_x if panel_idx == 0 else right_x
        data_dict = _build_data_dict(config, player_data)

        draw_professional_panel(
            draw,
            title=config["title"],
            data_dict=data_dict,
            xy=(x, panels_area_y),
            panel_size=(panel_w, panel_h),
            title_font=config["title_font"],
            value_color=config["value_color"],
            **panel_base_config,
        )

    # 绘制方格数据（3/4）
    row2_y = panels_area_y + panel_h + gap
    for panel_idx, config in enumerate(PANEL_CONFIGS[2:]):
        x = left_x if panel_idx == 0 else right_x
        data_dict = _build_data_dict(config, player_data)

        draw_professional_panel(
            draw,
            title=config["title"],
            data_dict=data_dict,
            xy=(x, row2_y),
            panel_size=(panel_w, panel_h),
            title_font=config["title_font"],
            value_color=config["value_color"],
            **panel_base_config,
        )

    return img


def create_minimal_stats_panel(
    width: int = MIN_PANEL_WIDTH,
    height: int = MIN_PANEL_HEIGHT,
    player_data: dict | None = None,
) -> Image.Image:
    """
    创建最小化统计面板（紧凑的水平卡片条）

    Args:
        width: 面板宽度（默认900px）
        height: 面板高度（默认150px）
        player_data: 玩家数据字典

    Returns:
        含4个关键统计卡片的面板图片
    """
    if player_data is None:
        player_data = {}

    img = Image.new("RGBA", (width, height), Colors.PROFESSIONAL_BG + (255,))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [0, 0, width, height],
        radius=10,
        outline=Colors.PROFESSIONAL_BORDER + (200,),
        width=2,
    )

    # 计算尺寸
    padding = MIN_PANEL_PADDING
    card_width = max(140, (width - padding * 5) // 4)
    card_height = height - padding * 2
    x_start = padding

    min_stats = [
        ("分数", "source", Colors.ACCENT_BLUE),
        ("击杀", "kills", Colors.ACCENT_GREEN),
        ("排名", "rank", Colors.ACCENT_YELLOW),
        ("爆头", "avg_headshots", Colors.ACCENT_RED),
    ]

    # 绘制
    for i, (label, key, color) in enumerate(min_stats):
        x = x_start + i * (card_width + padding)
        value = str(player_data.get(key, 0))
        value = value.replace("%", "") if isinstance(value, str) else str(value)

        draw_stat_card(
            draw,
            xy=(x, padding),
            size=(card_width, card_height),
            label=label,
            value=value,
            stat_font=l4_font_40,
            label_font=l4_font_40,
            label_color=Colors.TEXT_LIGHT_GRAY,
            value_color=color,
            bg_color=(255, 255, 255, 6),
            border_color=color + (140,),
        )

    return img
