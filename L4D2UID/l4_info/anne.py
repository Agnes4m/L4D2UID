import random
from typing import Union
from pathlib import Path

from PIL import Image, ImageDraw

from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import easy_paste, draw_pic_with_ring

from ..utils.l4_api import l4_api
from ..utils.l4_font import l4_font_20, l4_font_26, l4_font_30, l4_font_40
from ..utils.api.models import AnnePlayer2
from ..utils.error_reply import get_error

TEXTURED = Path(__file__).parent / "texture2d" / "anne"


def draw_title_section(img: Image.Image, title: str, y_pos: int) -> None:
    """绘制标题栏"""
    title_img = Image.open(TEXTURED / "title_bg.png").resize((900, 100))
    title_img_draw = ImageDraw.Draw(title_img)
    title_img_draw.text((50, 30), title, "white", font=l4_font_30)
    easy_paste(img, title_img, (0, y_pos))


def draw_data_row(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    font=l4_font_30,
    color: str = "white",
) -> None:
    """绘制单行数据"""
    draw.text((x, y), text, color, font=font)


async def get_anne_search_img(keyword: str) -> str:
    detail = await l4_api.search_player(keyword)

    # logger.info(detail)
    if isinstance(detail, int):
        return get_error(detail)

    search_len = len(detail)
    search_msg = f"搜索结果{search_len}个：\n"
    for i in range(min(search_len, 5)):
        search_msg += f"""
{i + 1}、{detail[i]["name"]} | {detail[i]["scoce"]} | {detail[i]["last_time"]}
{detail[i]["steamid"]}"""
    return search_msg


async def get_anne_player_img(keyword: str, head_img: Image.Image) -> Union[str, bytes]:
    detail = await l4_api.play_info(keyword)

    logger.info(detail)
    if isinstance(detail, int):
        return get_error(detail)
    if detail is None:
        return get_error(401)

    return await draw_anne_player_img(detail, head_img)


async def draw_anne_player_img(detail: AnnePlayer2, head_img: Image.Image):
    if len(detail) == 0:
        return get_error(1001)

    bg_path = list((TEXTURED / "bg").glob("*.png"))
    if bg_path:
        img = Image.open(random.choice(bg_path))
    else:
        raise FileNotFoundError("没有找到背景图像文件。")

    # 开头内容
    title_img = Image.open(TEXTURED / "title_bg.png").resize((900, 100))
    title_img_draw = ImageDraw.Draw(title_img)
    title_img_draw.text((220, 20), "求生之路-anne电信服查询", "white", font=l4_font_40)
    easy_paste(img, title_img, (0, 0))

    easy_paste(img, head_img.resize((100, 100)), (100, 180), direction="cc")

    title = Image.open(TEXTURED / "title.png").resize((530, 190))
    title_draw = ImageDraw.Draw(title)
    line = Image.open(TEXTURED / "line.png")
    easy_paste(title, line, (30, 20))
    logger.info(detail["info"]["avatar"])

    draw_data_row(
        title_draw,
        f"昵称：{detail['info']['name']}",
        70,
        20,
        l4_font_40,
        "black",
    )
    draw_data_row(
        title_draw,
        f"SteamID：{detail['info']['steamid']}",
        30,
        80,
        l4_font_26,
        "black",
    )
    draw_data_row(
        title_draw,
        f"上次在线：{detail['info']['lasttime']}",
        30,
        140,
        l4_font_20,
        "black",
    )

    easy_paste(img, title, (180, 110))

    anne_head = Image.open(TEXTURED / "anne_head.jpg").resize((100, 100))
    anne_img = await draw_pic_with_ring(anne_head, 100)
    easy_paste(img, anne_img, (800, 180), direction="cc")

    # 基础数据
    draw_title_section(img, "基础信息", 320)

    base_img = Image.open(TEXTURED / "base1.png").resize((800, 200))
    base_draw = ImageDraw.Draw(base_img)
    draw_data_row(base_draw, f"分数: {detail['detail']['source']}", 40, 20)
    draw_data_row(base_draw, f"击杀: {detail['detail']['kills']}", 40, 80)
    draw_data_row(
        base_draw,
        f"游戏时长: {detail['info']['playtime'].split('(')[0]}",
        40,
        140,
    )
    draw_data_row(base_draw, f"排名: {detail['detail']['rank']}", 440, 20)
    draw_data_row(base_draw, f"爆头率: {detail['detail']['avg_headshots']}", 440, 80)
    draw_data_row(base_draw, f"分数获取/分钟: {detail['detail']['avg_source']}", 440, 140)
    easy_paste(img, base_img, (40, 440))

    # 黑枪数据
    draw_title_section(img, "黑枪数据", 655)

    base_img = Image.open(TEXTURED / "base2.png").resize((800, 140))
    base_draw = ImageDraw.Draw(base_img)
    draw_data_row(base_draw, f"黑枪次数: {detail['error']['mistake_shout']}", 40, 20)
    draw_data_row(base_draw, f"击倒队友: {detail['error']['down_friend']}", 40, 80)
    draw_data_row(base_draw, f"杀死队友: {detail['error']['kill_friend']}", 440, 20)
    draw_data_row(base_draw, f"放弃队友: {detail['error']['abandon_friend']}", 440, 80)
    easy_paste(img, base_img, (40, 770))

    # 其他数据
    draw_title_section(img, "其他数据", 930)

    base_img = Image.open(TEXTURED / "base3.png").resize((800, 200))
    base_draw = ImageDraw.Draw(base_img)
    draw_data_row(base_draw, f"药丸赠与: {detail['sur']['pills_give']}", 40, 20)
    draw_data_row(base_draw, f"保护队友: {detail['sur']['protect_friend']}", 40, 80)
    draw_data_row(
        base_draw,
        f"秒妹数量: {detail['sur']['witch_instantly_kill']}",
        40,
        140,
    )
    draw_data_row(base_draw, f"拉起队友: {detail['sur']['friend_up']}", 440, 20)
    draw_data_row(base_draw, f"近战刀牛: {detail['sur']['melee_charge']}", 440, 80)
    draw_data_row(base_draw, f"地图完成: {detail['sur']['map_clear']}", 440, 140)
    easy_paste(img, base_img, (40, 1040))

    # 地图数据
    draw_title_section(img, "地图数据", 1260)

    return await convert_img(img)
