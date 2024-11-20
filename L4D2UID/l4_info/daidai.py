import random
from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import easy_paste, draw_pic_with_ring

from ..utils.l4_api import l4_api
from ..utils.error_reply import get_error
from ..utils.api.models import AnnePlayer2
from ..utils.l4_font import l4_font_20, l4_font_26, l4_font_30, l4_font_40

TEXTURED = Path(__file__).parent / "texture2d" / "anne"


async def get_daidai_player_img(
    keyword: str, head_img: Image.Image
) -> Union[str, bytes]:
    detail = await l4_api.play_info(keyword)

    logger.info(detail)
    if isinstance(detail, int):
        return get_error(detail)
    if detail is None:
        return get_error(401)

    return await draw_daidai_player_img(detail, head_img)

async def draw_daidai_player_img(detail: AnnePlayer2, head_img: Image.Image):
    if not detail:
        return get_error(1001)
    return "test success"