"""
PIL 图片美化工具库（combined utilities）

综合提供现代化设计风格的图片绘制增强功能和图片处理工具

模块功能：
- Colors: 统一的配色方案
- 图片加载和缓存: 统一的缓存机制和加载函数
- 高级绘制函数: 卡片、面板、进度条等高级绘制功能
- 图片处理工具: 文字渲染、图片合成、缩放、百分比转换等
"""

from typing import Tuple, Union, Optional, cast
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from gsuid_core.logger import logger
from gsuid_core.data_store import get_res_path
from gsuid_core.utils.image.utils import download_pic_to_image

_IMAGE_CACHE: dict[Path, Image.Image] = {}
"""图片缓存"""


# 颜色定义（现代调色板）
class Colors:
    """配色"""

    # 主色系
    PRIMARY = (70, 130, 180)  # 钢蓝色
    SECONDARY = (100, 149, 237)  # 矢车菊蓝

    # 文字
    TEXT_DARK = (45, 55, 72)  # 深灰/黑
    TEXT_LIGHT = (255, 255, 255)  # 白色
    TEXT_GRAY = (107, 114, 128)  # 中灰
    TEXT_LIGHT_GRAY = (156, 163, 175)  # 浅灰

    # 背景
    BG_LIGHT = (240, 244, 250)  # 浅蓝白
    BG_DARK = (15, 23, 42)  # 深蓝黑

    # 强调
    ACCENT_RED = (239, 68, 68)  # 红色
    ACCENT_GREEN = (34, 197, 94)  # 绿色
    ACCENT_YELLOW = (234, 179, 8)  # 金色
    ACCENT_BLUE = (59, 130, 246)  # 蓝色

    # 专业色
    PROFESSIONAL_BG = (248, 250, 252)  # 浅灰蓝背景
    PROFESSIONAL_CARD = (255, 255, 255)  # 白色卡片
    PROFESSIONAL_BORDER = (226, 232, 240)  # 边框色
    PROFESSIONAL_TITLE = (15, 23, 42)  # 标题色


def load_image(path: Path) -> Image.Image:
    """
    加载图片并自动缓存，避免重复I/O

    Args:
        path: 图片路径

    Returns:
        RGBA格式的图片对象（每次返回新副本）
    """
    if path not in _IMAGE_CACHE:
        img = Image.open(path)
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        _IMAGE_CACHE[path] = img
    return _IMAGE_CACHE[path].copy()


def create_rounded_rectangle(
    size: Tuple[int, int],
    radius: int = 15,
    fill: Tuple[int, int, int, int] = (255, 255, 255, 200),
    outline: Optional[Tuple[int, int, int, int]] = None,
    outline_width: int = 1,
) -> Image.Image:
    """
    创建圆角矩形图片

    Args:
        size: 图片尺寸 (width, height)
        radius: 圆角半径
        fill: 填充颜色 RGBA
        outline: 边框颜色 RGBA，None 则无边框
        outline_width: 边框宽度

    Returns:
        PIL Image 对象
    """
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    x, y = 0, 0
    w, h = size

    draw.arc([x, y, x + radius * 2, y + radius * 2], 180, 270, fill=fill, width=outline_width)
    draw.arc([w - radius * 2, y, w, y + radius * 2], 270, 360, fill=fill, width=outline_width)
    draw.arc([x, h - radius * 2, x + radius * 2, h], 90, 180, fill=fill, width=outline_width)
    draw.arc([w - radius * 2, h - radius * 2, w, h], 0, 90, fill=fill, width=outline_width)

    draw.rectangle([x + radius, y, w - radius, y + h], fill=fill)
    draw.rectangle([x, y + radius, w, h - radius], fill=fill)

    # 边框
    if outline:
        draw.arc([x, y, x + radius * 2, y + radius * 2], 180, 270, fill=outline, width=outline_width)
        draw.arc([w - radius * 2, y, w, y + radius * 2], 270, 360, fill=outline, width=outline_width)
        draw.arc([x, h - radius * 2, x + radius * 2, h], 90, 180, fill=outline, width=outline_width)
        draw.arc([w - radius * 2, h - radius * 2, w, h], 0, 90, fill=outline, width=outline_width)

    return img


def add_shadow(
    img: Image.Image,
    offset: Tuple[int, int] = (3, 3),
    blur_radius: int = 8,
    shadow_color: Tuple[int, int, int] = (0, 0, 0),
    shadow_opacity: int = 100,
) -> Image.Image:
    """
    为图片添加阴影效果

    Args:
        img: 输入图片
        offset: 阴影偏移 (x, y)
        blur_radius: 模糊半径
        shadow_color: 阴影颜色 RGB
        shadow_opacity: 阴影透明度 (0-255)

    Returns:
        带阴影的图片
    """

    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)

    x, y = offset
    w, h = img.size
    shadow_draw.rectangle([x, y, x + w, y + h], fill=shadow_color + (shadow_opacity,))

    result = Image.new("RGBA", img.size, (0, 0, 0, 0))
    result.paste(shadow, (0, 0), shadow)
    result.paste(img, (0, 0), img)

    return result


def create_gradient_background(
    size: Tuple[int, int],
    color_start: Tuple[int, int, int],
    color_end: Tuple[int, int, int],
    direction: str = "vertical",
) -> Image.Image:
    """
    创建渐变背景

    Args:
        size: 背景尺寸 (width, height)
        color_start: 起始颜色 RGB
        color_end: 结束颜色 RGB
        direction: 方向 'vertical' 或 'horizontal'

    Returns:
        渐变背景图片
    """
    img = Image.new("RGB", size)
    pixels = img.load()

    w, h = size

    if direction == "vertical":
        for y in range(h):
            # 计算当前行的颜色
            ratio = y / h
            r = int(color_start[0] * (1 - ratio) + color_end[0] * ratio)
            g = int(color_start[1] * (1 - ratio) + color_end[1] * ratio)
            b = int(color_start[2] * (1 - ratio) + color_end[2] * ratio)

            for x in range(w):
                pixels[x, y] = (r, g, b)
    else:  # horizontal
        for x in range(w):
            ratio = x / w
            r = int(color_start[0] * (1 - ratio) + color_end[0] * ratio)
            g = int(color_start[1] * (1 - ratio) + color_end[1] * ratio)
            b = int(color_start[2] * (1 - ratio) + color_end[2] * ratio)

            for y in range(h):
                pixels[x, y] = (r, g, b)

    return img


def draw_text_with_shadow(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: Tuple[int, int] | Tuple[float, float],
    font: ImageFont.FreeTypeFont,
    fill: Tuple[int, int, int, int] = (255, 255, 255, 255),
    shadow_offset: Tuple[int, int] = (2, 2),
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 100),
) -> None:
    """
    绘制带阴影的文本

    Args:
        draw: ImageDraw 对象
        text: 文本内容
        xy: 文本位置 (x, y)
        font: 字体
        fill: 文字颜色 RGBA
        shadow_offset: 阴影偏移
        shadow_color: 阴影颜色 RGBA
    """
    x, y = xy
    sx, sy = shadow_offset

    draw.text((x + sx, y + sy), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=fill)


def draw_divider_line(
    draw: ImageDraw.ImageDraw,
    start_xy: Tuple[int, int],
    end_xy: Tuple[int, int],
    width: int = 1,
    fill: Tuple[int, int, int, int] = (200, 200, 200, 100),
) -> None:
    """
    绘制分割线

    Args:
        draw: ImageDraw 对象
        start_xy: 起点 (x, y)
        end_xy: 终点 (x, y)
        width: 线条宽度
        fill: 线条颜色 RGBA
    """
    draw.line([start_xy, end_xy], fill=fill, width=width)


def draw_styled_box(
    img: Image.Image,
    xy: Tuple[int, int],
    size: Tuple[int, int],
    title: Optional[str] = None,
    title_font: Optional[ImageFont.FreeTypeFont] = None,
    bg_color: Tuple[int, int, int, int] = (240, 244, 250, 255),
    title_color: Tuple[int, int, int] = (70, 130, 180),
    border_color: Tuple[int, int, int, int] = (200, 210, 230, 150),
    border_width: int = 1,
    corner_radius: int = 10,
) -> Image.Image:
    """
    绘制样式化的盒子（含标题）

    Args:
        img: 目标图片
        xy: 盒子位置 (x, y)
        size: 盒子大小 (width, height)
        title: 标题文本
        title_font: 标题字体
        bg_color: 背景颜色 RGBA
        title_color: 标题颜色 RGB
        border_color: 边框颜色 RGBA
        border_width: 边框宽度
        corner_radius: 圆角半径

    Returns:
        修改后的图片
    """
    x, y = xy
    w, h = size

    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [x, y, x + w, y + h], radius=corner_radius, fill=bg_color, outline=border_color, width=border_width
    )

    # 绘制标题
    if title and title_font:
        title_height = 35
        # 标题背景条
        draw.rounded_rectangle([x, y, x + w, y + title_height], radius=corner_radius, fill=title_color + (220,))

        # 标题文字
        bbox = draw.textbbox((0, 0), title, font=title_font)
        text_w = bbox[2] - bbox[0]
        text_x = x + (w - text_w) // 2
        text_y = y + (title_height - (bbox[3] - bbox[1])) // 2

        draw.text((text_x, text_y), title, font=title_font, fill=(255, 255, 255))
        draw.line([x + 10, y + title_height, x + w - 10, y + title_height], fill=(255, 255, 255, 50), width=1)

    return img


def create_modern_card(
    width: int = 400,
    height: int = 200,
    title: str = "Card Title",
    title_font: Optional[ImageFont.FreeTypeFont] = None,
    content_lines: Optional[list[str]] = None,
    content_font: Optional[ImageFont.FreeTypeFont] = None,
) -> Image.Image:
    """
    创建现代化卡片

    Args:
        width: 卡片宽度
        height: 卡片高度
        title: 卡片标题
        title_font: 标题字体
        content_lines: 内容行列表
        content_font: 内容字体

    Returns:
        卡片图片
    """
    img = create_gradient_background((width, height), Colors.BG_LIGHT, (220, 230, 245), direction="vertical")
    img = img.convert("RGBA")

    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [10, 10, width - 10, height - 10],
        radius=15,
        fill=(255, 255, 255, 240),
        outline=Colors.SECONDARY + (150,),
        width=2,
    )

    # 绘制标题
    if title_font:
        title_text = title
        bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_w = bbox[2] - bbox[0]
        title_x = (width - title_w) // 2
        draw.text((title_x, 20), title_text, font=title_font, fill=Colors.PRIMARY)
        draw.line([30, 50, width - 30, 50], fill=Colors.SECONDARY + (100,), width=2)

    # 绘制内容
    if content_lines and content_font:
        y_offset = 70
        for line in content_lines:
            bbox = draw.textbbox((0, 0), line, font=content_font)
            line_h = bbox[3] - bbox[1]
            draw.text((30, y_offset), line, font=content_font, fill=Colors.TEXT_DARK)
            y_offset += line_h + 10

    return img


def draw_professional_panel(
    draw: ImageDraw.ImageDraw,
    title: str,
    data_dict: dict,
    xy: Tuple[int, int],
    panel_size: Tuple[int, int],
    title_font: ImageFont.FreeTypeFont,
    label_font: ImageFont.FreeTypeFont,
    value_font: ImageFont.FreeTypeFont,
    title_color: Tuple[int, int, int] = Colors.PROFESSIONAL_TITLE,
    label_color: Tuple[int, int, int] = Colors.TEXT_LIGHT_GRAY,
    value_color: Tuple[int, int, int] = Colors.PRIMARY,
    bg_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    border_color: Tuple[int, int, int, int] = (226, 232, 240, 200),
) -> None:
    """
    绘制专业数据面板

    Args:
        draw: ImageDraw 对象
        title: 面板标题
        data_dict: 数据字典 {label: value}
        xy: 面板位置 (x, y)
        panel_size: 面板大小 (width, height)
        title_font: 标题字体
        label_font: 标签字体
        value_font: 数值字体
        title_color: 标题颜色 RGB
        label_color: 标签颜色 RGB
        value_color: 数值颜色 RGB
        bg_color: 背景色 RGBA
        border_color: 边框色 RGBA
    """
    x, y = xy
    w, h = panel_size

    draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=12,
        fill=bg_color,
        outline=border_color,
        width=1,
    )

    # 标题
    title_height = 45
    draw.rounded_rectangle(
        [x, y, x + w, y + title_height],
        radius=12,
        fill=title_color + (8,),
    )
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height_text = title_bbox[3] - title_bbox[1]
    title_x = x + (w - title_width) // 2
    title_y = y + (title_height - title_height_text) // 2
    draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255))

    # 数据行
    y_offset = y + title_height + 15
    row_height = int((h - title_height - 30) / len(data_dict) * 1.1)

    for i, (label, value) in enumerate(data_dict.items()):
        row_y = y_offset + i * row_height

        # 标签
        draw.text((x + 20, row_y), label, font=label_font, fill=label_color)
        value_text = str(value)
        value_bbox = draw.textbbox((0, 0), value_text, font=value_font)
        value_w = value_bbox[2] - value_bbox[0]
        value_x = x + w - value_w - 20
        draw.text((value_x, row_y), value_text, font=value_font, fill=value_color)

        # 分割线
        if i < len(data_dict) - 1:
            line_y = row_y + row_height - 5
            draw.line(
                [x + 20, line_y, x + w - 20, line_y],
                fill=Colors.PROFESSIONAL_BORDER + (100,),
                width=1,
            )


def draw_stat_card(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int],
    size: Tuple[int, int],
    label: str,
    value: str,
    stat_font: ImageFont.FreeTypeFont,
    label_font: ImageFont.FreeTypeFont,
    label_color: Tuple[int, int, int] = Colors.TEXT_LIGHT_GRAY,
    value_color: Tuple[int, int, int] = Colors.ACCENT_BLUE,
    bg_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    border_color: Optional[Tuple[int, int, int, int]] = None,
) -> None:
    """
    绘制统计卡片（突出数值显示）

    Args:
        draw: ImageDraw 对象
        xy: 位置 (x, y)
        size: 卡片大小 (width, height)
        label: 标签文本
        value: 数值文本
        stat_font: 数值字体（大）
        label_font: 标签字体（小）
        label_color: 标签颜色 RGB
        value_color: 数值颜色 RGB
        bg_color: 背景色 RGBA
        border_color: 边框色 RGBA
    """
    x, y = xy
    w, h = size

    # 绘制背景
    draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=8,
        fill=bg_color,
        outline=border_color or Colors.PROFESSIONAL_BORDER + (100,),
        width=1,
    )

    # 绘制标签
    label_bbox = draw.textbbox((0, 0), label, font=label_font)
    label_x = x + (w - (label_bbox[2] - label_bbox[0])) // 2
    label_y = y + 12
    draw.text((label_x, label_y), label, font=label_font, fill=label_color)

    value_bbox = draw.textbbox((0, 0), value, font=stat_font)
    value_w = value_bbox[2] - value_bbox[0]
    value_x = x + (w - value_w) // 2
    value_y = y + h - 75
    draw.text((value_x, value_y), value, font=stat_font, fill=value_color)


async def save_img(img_url: str, img_type: str, size: Optional[Tuple[int, int]] = None):
    """下载图片并缓存以读取"""
    map_img = Image.new("RGBA", (200, 600), (0, 0, 0, 255))
    img_path = get_res_path("L4D2UID") / img_type / img_url.split("/")[-1]
    img_path.parent.mkdir(parents=True, exist_ok=True)
    if not img_path.is_file():
        for i in range(3):
            try:
                map_img = await download_pic_to_image(img_url)
                if map_img.mode != "RGBA":
                    map_img = map_img.convert("RGBA")
                if map_img:
                    map_img.save(img_path)
                    break
                logger.warning(f"图片下载错误，正在尝试第{i + 2}次")
                if i == 2:
                    raise Exception("图片下载失败！")
            except Exception:
                continue

    else:
        map_img = Image.open(img_path)
        if map_img.mode != "RGBA":
            map_img = map_img.convert("RGBA")
    if size:
        map_img = map_img.resize(size)
    return map_img


def draw_title_section(
    img: Image.Image,
    title: str,
    y_pos: int,
    title_bg_path: Path,
    font: ImageFont.FreeTypeFont,
    text_pos: Tuple[int, int] = (-1, 30),
    text_color: str = "white",
) -> None:
    """
    绘制标题栏 - 通用工具

    Args:
        img: 目标图片
        title: 标题文本
        y_pos: 贴到图片的 Y 位置
        title_bg_path: 标题背景图路径
        font: 标题字体
        text_pos: 文字在背景中的位置 (x, y)，x 为 -1 时自动居中
        text_color: 文字颜色
    """
    from gsuid_core.utils.image.image_tools import easy_paste

    title_img = load_image(title_bg_path).resize((900, 100))
    title_img_draw = ImageDraw.Draw(title_img)

    text_x, text_y = text_pos
    if text_x == -1:
        text_bbox = title_img_draw.textbbox((0, 0), title, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (900 - text_width) // 2

    title_img_draw.text((text_x, text_y), title, text_color, font=font)
    easy_paste(img, title_img, (0, y_pos))


def draw_text_row(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    color: Union[str, Tuple[int, int, int]] = "white",
) -> None:
    """
    绘制单行文字（带阴影）- 通用工具

    Args:
        draw: ImageDraw 对象
        text: 文本内容
        x: X 位置
        y: Y 位置
        font: 字体
        color: 颜色 (支持颜色名或 RGB 元组)
    """
    # 颜色映射表
    color_map = {
        "white": (255, 255, 255, 255),
        "black": (0, 0, 0, 255),
        "gray": (128, 128, 128, 255),
        "light_gray": Colors.TEXT_LIGHT_GRAY + (255,),
    }
    if isinstance(color, str):
        fill_color = color_map.get(color, Colors.TEXT_LIGHT + (255,))
        shadow_color = (255, 255, 255, 80) if color == "black" else (50, 50, 50, 120)
    elif isinstance(color, tuple) and len(color) == 3:
        fill_color = cast(Tuple[int, int, int, int], color + (255,))
        shadow_color = (255, 255, 255, 80)  # 亮文字用深阴影
    else:
        fill_color = Colors.TEXT_LIGHT + (255,)
        shadow_color = (50, 50, 50, 120)

    draw_text_with_shadow(
        draw,
        text,
        (x, y),
        font,
        fill=fill_color,
        shadow_offset=(2, 2),
        shadow_color=shadow_color,
    )
