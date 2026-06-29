from pathlib import Path
from typing import Optional, Tuple, Union, cast

from gsuid_core.data_store import get_res_path
from gsuid_core.logger import logger
from gsuid_core.utils.image.utils import download_pic_to_image
from PIL import Image, ImageDraw, ImageFont

_IMAGE_CACHE: dict[Path, Image.Image] = {}


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
