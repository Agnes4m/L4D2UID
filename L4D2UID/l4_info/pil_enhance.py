"""
PIL 图片美化工具
提供现代化设计风格的图片绘制增强功能
"""

from typing import Tuple, Optional

from PIL import Image, ImageDraw, ImageFont


# 颜色定义（现代调色板）
class Colors:
    """现代化配色方案"""

    # 主色系
    PRIMARY = (70, 130, 180)  # 钢蓝色
    SECONDARY = (100, 149, 237)  # 矢车菊蓝

    # 文字色系
    TEXT_DARK = (45, 55, 72)  # 深灰/黑
    TEXT_LIGHT = (255, 255, 255)  # 白色
    TEXT_GRAY = (107, 114, 128)  # 中灰

    # 背景色系
    BG_LIGHT = (240, 244, 250)  # 浅蓝白
    BG_DARK = (15, 23, 42)  # 深蓝黑

    # 强调色
    ACCENT_RED = (239, 68, 68)  # 红色
    ACCENT_GREEN = (34, 197, 94)  # 绿色
    ACCENT_YELLOW = (234, 179, 8)  # 金色


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

    # 边界坐标
    x, y = 0, 0
    w, h = size

    # 绘制圆角矩形
    # 四个圆角
    draw.arc([x, y, x + radius * 2, y + radius * 2], 180, 270, fill=fill, width=outline_width)
    draw.arc([w - radius * 2, y, w, y + radius * 2], 270, 360, fill=fill, width=outline_width)
    draw.arc([x, h - radius * 2, x + radius * 2, h], 90, 180, fill=fill, width=outline_width)
    draw.arc([w - radius * 2, h - radius * 2, w, h], 0, 90, fill=fill, width=outline_width)

    # 四条直线
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
    # 创建阴影层
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)

    # 绘制阴影
    x, y = offset
    w, h = img.size
    shadow_draw.rectangle([x, y, x + w, y + h], fill=shadow_color + (shadow_opacity,))

    # 应用模糊（简化版：多层透明度）
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
    xy: Tuple[int, int],
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

    # 先绘制阴影
    draw.text((x + sx, y + sy), text, font=font, fill=shadow_color)
    # 再绘制文字
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

    # 绘制圆角矩形背景
    draw.rounded_rectangle(
        [x, y, x + w, y + h], radius=corner_radius, fill=bg_color, outline=border_color, width=border_width
    )

    # 绘制标题（如果有）
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

        # 标题下分割线
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
    # 创建渐变背景
    img = create_gradient_background((width, height), Colors.BG_LIGHT, (220, 230, 245), direction="vertical")
    img = img.convert("RGBA")

    draw = ImageDraw.Draw(img)

    # 绘制card容器
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

        # 标题下的装饰线
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
