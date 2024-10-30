from pathlib import Path
from typing import Optional, Tuple, Union

from gsuid_core.data_store import get_res_path
from gsuid_core.logger import logger
from gsuid_core.utils.image.image_tools import draw_text_by_line
from gsuid_core.utils.image.utils import download_pic_to_image
from PIL import Image, ImageDraw, ImageFont

from ..utils.l4_font import FONT_MAIN_PATH, FONT_TIELE_PATH

TEXTURE = Path(__file__).parent / "texture2d"


ICON_PATH = Path(__file__).parent / "texture2d/icon"
font_head = ImageFont.truetype(str(FONT_TIELE_PATH), 20)
font_main = ImageFont.truetype(str(FONT_MAIN_PATH), 20)


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
                logger.warning(f"图片下载错误，正在尝试第{i+2}次")
                if i == 2:
                    raise Exception("图片下载失败！")
            except Exception:
                continue

    else:

        map_img = Image.open(img_path)
        if map_img.mode != "RGBA":
            map_img = map_img.convert("RGBA")
    if size:
        map_img.resize(size)
    return map_img


async def paste_img(
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
    """贴文字"""
    # draw = ImageDraw.Draw(img)

    # 字体
    if fonts == "head":
        font = ImageFont.truetype(str(FONT_TIELE_PATH), size)
    else:
        font = ImageFont.truetype(str(FONT_MAIN_PATH), size)

    # 行数
    aa, ab, ba, bb = font.getbbox(msg)
    if is_mid:
        site_x = round((long[1] - long[0] - ba + aa) / 2)
    else:
        site_x = site[0]

    if is_white:
        s = 160
    else:
        s = 0
    # 绘制白色矩形遮罩
    rect_color = (255, 255, 255, 128)
    site_white = (
        site_x + aa - 5,
        site[1] + ab,
        site_x + ba + 5,
        site[1] + bb + 7,
    )
    mask = Image.new("RGBA", (int(ba - aa + 5), int(bb - ab + 5)), (255, 255, 255, s))
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rectangle(site_white, fill=rect_color)

    draw_mask.text(xy=(0, 0), text=msg, font=font, fill=color)
    img.paste(mask, site, mask)


async def simple_paste_img(
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
    if size == 20:
        if fonts == "head":
            font = font_head
        else:
            font = font_main
    else:
        if fonts == "head":
            font = ImageFont.truetype(str(FONT_TIELE_PATH), size)
        else:
            font = ImageFont.truetype(str(FONT_MAIN_PATH), size)
    draw = ImageDraw.Draw(img)
    draw.text(site, msg, fill=color, font=font)
    # 以后替换
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


async def resize_image_to_percentage(img: Image.Image, percentage: float):
    """图片缩放"""
    width, height = img.size
    new_width = int(width * percentage / 100)
    new_height = int(height * percentage / 100)
    out_img = Image.new("RGBA", (new_width, new_height), color=(255, 255, 255, 255))
    pic_new = img.resize((new_width, new_height))
    out_img.paste(pic_new)
    return out_img


async def load_groudback(bg_img_path: Path | Image.Image, alpha_percent: float = 0.5):
    """加载背景图
    透明一半"""
    if isinstance(bg_img_path, Path):
        first_img = Image.open(bg_img_path)
        if first_img.mode != "RGBA":
            first_img = first_img.convert("RGBA")
    else:
        first_img = bg_img_path
    transparent_img = Image.new(
        "RGBA", first_img.size, (255, 255, 255, int(255 * alpha_percent))
    )
    first_img.paste(transparent_img, None, transparent_img)

    return first_img


async def percent_to_img(percent: float, size: tuple = (211, 46)):
    """由半分比转化为图"""
    # 31*46
    img_none = Image.open(ICON_PATH / "none.png")
    img_yellow = Image.open(ICON_PATH / "yellow.png")
    img_out = Image.new("RGBA", (211, 46), (0, 0, 0, 0))
    for i in range(10):
        if percent > 0:
            img_out.paste(img_yellow, (i * 20, 0), img_yellow)
        else:
            img_out.paste(img_none, (i * 20, 0), img_none)
        percent -= 0.1
    return img_out.resize(size)
