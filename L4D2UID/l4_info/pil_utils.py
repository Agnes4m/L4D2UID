import math
import random
from pathlib import Path
from typing import Optional

from PIL import Image

_IMAGE_CACHE: dict[Path, Image.Image] = {}


def prepare_bg(
    texture_dir: Optional[Path] = None,
    w: int = 900,
    h: int = 1200,
) -> Image.Image:
    """创建背景图：不拉伸，宽度固定，高度不够则平铺、超出则居中裁剪"""
    if texture_dir is None:
        texture_dir = Path(__file__).parent / "texture2d" / "anne" / "bg"
    bg_files = list(texture_dir.glob("*.png"))
    if not bg_files:
        bg = Image.new("RGBA", (w, h), (10, 14, 23))
        overlay = Image.new("RGBA", bg.size, (10, 14, 23, 210))
        return Image.alpha_composite(bg, overlay)

    src = Image.open(random.choice(bg_files)).convert("RGBA")
    sw, sh = src.size

    # 1. 按宽度缩放（保持比例）
    ratio = w / sw
    new_w = w
    new_h = int(sh * ratio)
    src = src.resize((new_w, new_h), Image.LANCZOS)

    # 2. 高度处理
    if new_h < h:
        # 平铺至足够高度
        tiles = math.ceil(h / new_h)
        canvas = Image.new("RGBA", (w, new_h * tiles))
        for i in range(tiles):
            canvas.paste(src, (0, i * new_h))
        src = canvas
        # 从顶部开始裁剪
        src = src.crop((0, 0, w, h))
    elif new_h > h:
        # 居中裁剪
        top = (new_h - h) // 2
        src = src.crop((0, top, w, top + h))

    overlay = Image.new("RGBA", (w, h), (10, 14, 23, 210))
    return Image.alpha_composite(src, overlay)


class Colors:
    PRIMARY = (56, 189, 248)
    SECONDARY = (45, 212, 191)
    TEXT_DARK = (226, 232, 240)
    TEXT_LIGHT = (226, 232, 240)
    TEXT_GRAY = (107, 114, 128)
    TEXT_LIGHT_GRAY = (148, 163, 184)
    BG_LIGHT = (17, 24, 39)
    BG_DARK = (10, 14, 23)
    ACCENT_BLUE = (56, 189, 248)
    ACCENT_CYAN = (56, 189, 248)
    ACCENT_TEAL = (45, 212, 191)
    ACCENT_RED = (251, 113, 133)
    ACCENT_GREEN = (52, 211, 153)
    ACCENT_YELLOW = (250, 204, 21)
    ACCENT_PURPLE = (167, 139, 250)
    PROFESSIONAL_BG = (17, 24, 39)
    PROFESSIONAL_CARD = (17, 24, 39)
    PROFESSIONAL_BORDER = (55, 65, 81)
    PROFESSIONAL_TITLE = (56, 189, 248)


def load_image(path: Path) -> Image.Image:
    if path not in _IMAGE_CACHE:
        img = Image.open(path)
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        _IMAGE_CACHE[path] = img
    return _IMAGE_CACHE[path].copy()
