"""
生成 L4D2UID Footer 文件的脚本
生成 1000×30 像素的透明背景 footer 图片
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def generate_footer(
    text: str = "Create By GsCore & Power By L4D2UID",
    width: int = 1000,
    height: int = 30,
    text_color: tuple = (255, 255, 255),
    font_size: int = 16,
) -> Image.Image:
    """
    生成 footer 图片

    Args:
        text: footer 文本内容
        width: 图片宽度（像素）
        height: 图片高度（像素）
        text_color: 文本颜色 (R, G, B)
        font_size: 字体大小

    Returns:
        PIL Image 对象
    """
    # 创建透明背景图片 (RGBA 格式)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 获取默认字体，如果失败则使用无字体
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except (OSError, IOError):
        # 使用内置字体作为备选
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    # 获取文本的边界框以计算位置
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 计算文本居中位置（水平和垂直）
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # 添加文带透明度的文本
    text_color_rgba = text_color + (255,) if len(text_color) == 3 else text_color

    # 绘制文本
    draw.text((x, y), text, font=font, fill=text_color_rgba)

    return img


def save_footer(
    output_path: Path = None,
    text: str = "Create  By  GsCore  &  Power  By  L4D2UID",
    width: int = 1000,
    height: int = 30,
    text_color: tuple = (255, 255, 255),
    font_size: int = 24,
) -> Path:
    """
    生成并保存 footer 图片

    Args:
        output_path: 输出文件路径，默认为项目的 texture2d 目录
        text: footer 文本内容
        width: 图片宽度（像素）
        height: 图片高度（像素）
        text_color: 文本颜色 (R, G, B)
        font_size: 字体大小

    Returns:
        保存的文件路径
    """
    # 如果没有指定输出路径，使用默认路径
    if output_path is None:
        output_path = Path(__file__).parent / "footer.png"

    # 创建输出目录
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 生成图片
    img = generate_footer(text, width, height, text_color, font_size)

    # 保存图片
    img.save(output_path, "PNG")
    print(f"✓ Footer 已生成: {output_path}")
    print(f"  尺寸: {width}×{height} 像素")
    print(f"  内容: {text}")

    return output_path


if __name__ == "__main__":
    # 生成 footer 文件
    save_footer()
