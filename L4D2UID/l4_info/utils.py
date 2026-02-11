from typing import Tuple, Union, Optional
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from gsuid_core.logger import logger
from gsuid_core.data_store import get_res_path
from gsuid_core.utils.image.utils import download_pic_to_image
from gsuid_core.utils.image.image_tools import draw_text_by_line

from ..utils.l4_font import l4_font_20, l4_font_32
from .pil_enhance import Colors, draw_text_with_shadow, draw_divider_line

TEXTURE = Path(__file__).parent / "texture2d"


ICON_PATH = Path(__file__).parent / "texture2d/icon"
font_head = l4_font_20
font_main = l4_font_32

# 图片缓存
_image_cache: dict[Path, Image.Image] = {}


def _load_cached_image(path: Path) -> Image.Image:
    """加载缓存的图片，避免重复打开文件"""
    if path not in _image_cache:
        img = Image.open(path)
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        _image_cache[path] = img
    return _image_cache[path].copy()


async def save_img(img_url: str, img_type: str, size: Optional[Tuple[int, int]] = None):
    """下载图片并缓存以读取"""
    map_img = Image.new("RGBA", (200, 600), (0, 0, 0, 255))
    img_path = get_res_path("CS2UID") / img_type / img_url.split("/")[-1]
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


def paste_img(
    img: Image.Image,
    msg: str,
    size: int,
    site: Tuple[int, int] = (0, 0),
    is_mid: bool = False,
    fonts: Optional[str] = None,
    long: Tuple[int, int] = (0, 900),
    color: Union[Tuple[int, int, int, int], str] = (0, 0, 0, 255),
    is_white: bool = True,
):
    """贴文字 - 现代化版本（含圆角背景和阴影）"""
    # 字体选择
    font = font_head if fonts == "head" else font_main

    # 计算文字位置
    aa, ab, ba, bb = font.getbbox(msg)
    if is_mid:
        site_x = round((long[1] - long[0] - ba + aa) / 2)
    else:
        site_x = site[0]

    # 背景透明度
    bg_opacity = 160 if is_white else 0

    # 创建遮罩层（带圆角背景和阴影）
    mask_width = int(ba - aa + 10)
    mask_height = int(bb - ab + 10)
    mask = Image.new("RGBA", (mask_width, mask_height), (0, 0, 0, 0))
    draw_mask = ImageDraw.Draw(mask)

    # 绘制圆角背景矩形（现代化设计）
    bg_color = (255, 255, 255, bg_opacity)
    draw_mask.rounded_rectangle(
        [0, 0, mask_width - 1, mask_height - 1],
        radius=5,
        fill=bg_color,
        outline=(200, 200, 200, 100),
        width=1
    )

    # 转换颜色格式
    if isinstance(color, str):
        color_rgba = color
    else:
        color_rgba = color if len(color) == 4 else color + (255,)

    # 绘制带阴影的文字
    text_x = 5 - aa
    text_y = 5 - ab
    draw_text_with_shadow(
        draw_mask,
        msg,
        (text_x, text_y),
        font,
        fill=color_rgba if isinstance(color_rgba, tuple) and len(color_rgba) == 4 else Colors.TEXT_DARK + (255,),
        shadow_offset=(1, 1),
        shadow_color=(0, 0, 0, 80)
    )

    # 粘贴到主图片
    img.paste(mask, (site_x, site[1]), mask)


def simple_paste_img(
    img: Image.Image,
    msg: str,
    site: Tuple[int, int],
    size: int = 20,
    fonts: Optional[str] = None,
    color: Union[Tuple[int, int, int, int], str] = (0, 0, 0, 255),
    max_length: int = 1000,
    center: bool = False,
    line_space: Optional[float] = None,
):
    """无白框贴文字"""
    # 选择字体（统一使用预加载字体）
    font = font_head if fonts == "head" else font_main

    # 使用 draw_text_by_line 绘制（已包含基础文本和换行处理）
    draw_text_by_line(
        img=img,
        pos=site,
        text=msg,
        font=font,
        fill=color,
        max_length=max_length,
        center=center,
        line_space=line_space,
    )


def resize_image_to_percentage(img: Image.Image, percentage: float):
    """图片缩放"""
    width, height = img.size
    new_width = int(width * percentage / 100)
    new_height = int(height * percentage / 100)
    return img.resize((new_width, new_height))


def load_groudback(bg_img_path: Path | Image.Image, alpha_percent: float = 0.5):
    """加载背景图 - 透明化处理"""
    if isinstance(bg_img_path, Path):
        first_img = Image.open(bg_img_path)
        if first_img.mode != "RGBA":
            first_img = first_img.convert("RGBA")
    else:
        first_img = bg_img_path
    transparent_img = Image.new("RGBA", first_img.size, (255, 255, 255, int(255 * alpha_percent)))
    first_img.paste(transparent_img, None, transparent_img)
    return first_img


def percent_to_img(percent: float, size: tuple = (211, 46)):
    """由百分比转化为图"""
    img_none = _load_cached_image(ICON_PATH / "none.png")
    img_yellow = _load_cached_image(ICON_PATH / "yellow.png")
    img_out = Image.new("RGBA", (211, 46), (0, 0, 0, 0))

    for i in range(10):
        img = img_yellow if percent > 0 else img_none
        img_out.paste(img, (i * 20, 0), img)
        percent -= 0.1

    return img_out.resize(size)
