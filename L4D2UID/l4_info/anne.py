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


async def get_anne_search_img(keyword: str) -> str:
    detail = await l4_api.search_player(keyword)

    # logger.info(detail)
    if isinstance(detail, int):
        return get_error(detail)

    search_len = len(detail)
    search_msg = f"搜索结果{search_len}个：\n"
    for i in range(min(search_len, 5)):
        search_msg += f"""
{i+1}、{detail[i]['name']} | {detail[i]['scoce']} | {detail[i]['last_time']}
{detail[i]['steamid']}"""
    return search_msg


async def get_anne_player_img(
    keyword: str, head_img: Image.Image
) -> Union[str, bytes]:
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

    bg_path = list((TEXTURED / "bg").glob('*.png'))
    logger.info(bg_path)
    if bg_path:
        img = Image.open(random.choice(bg_path))
    else:
        raise FileNotFoundError("没有找到背景图像文件。")

    # 开头内容
    title_img = Image.open(TEXTURED / "title_bg.png").resize((900, 100))
    title_img_draw = ImageDraw.Draw(title_img)
    title_img_draw.text(
        (220, 20), "求生之路-anne电信服查询", "white", font=l4_font_40
    )
    easy_paste(img, title_img, (0, 0))

    easy_paste(img, head_img.resize((100, 100)), (100, 180), direction="cc")

    title = Image.open(TEXTURED / "title.png").resize((530, 190))
    title_draw = ImageDraw.Draw(title)
    line = Image.open(TEXTURED / "line.png")
    easy_paste(title, line, (30, 20))
    logger.info(detail['info']['avatar'])
    title_draw.text(
        (70, 20), f"昵称：{detail['info']['name']}", "black", font=l4_font_40
    )
    title_draw.text(
        (30, 80),
        f"SteamID：{detail['info']['steamid']}",
        "black",
        font=l4_font_26,
    )
    title_draw.text(
        (30, 140),
        f"上次在线：{detail['info']['lasttime']}",
        "black",
        font=l4_font_20,
    )
    easy_paste(img, title, (180, 110))

    anne_head = Image.open(TEXTURED / "anne_head.jpg").resize((100, 100))
    anne_img = await draw_pic_with_ring(anne_head, 100)
    easy_paste(img, anne_img, (800, 180), direction="cc")

    # 基础数据
    title_img = Image.open(TEXTURED / "title_bg.png").resize((900, 100))
    title_img_draw = ImageDraw.Draw(title_img)
    title_img_draw.text((50, 30), "基础信息", "white", font=l4_font_30)
    easy_paste(img, title_img, (0, 320))

    base_img = Image.open(TEXTURED / "base1.png").resize((800, 200))
    base_draw = ImageDraw.Draw(base_img)
    base_draw.text(
        (40, 20),
        f"分数: {detail['detail']['source']}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (40, 80),
        f"击杀: {detail['detail']['kills']}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (40, 140),
        f"游戏时长: {detail['info']['playtime'].split('(')[0]}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (440, 20),
        f"排名: {detail['detail']['rank']}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (440, 80),
        f"爆头率: {detail['detail']['avg_headshots']}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (440, 140),
        f"分数获取/分钟: {detail['detail']['avg_source']}",
        "white",
        font=l4_font_30,
    )
    easy_paste(img, base_img, (40, 440))

    # 黑枪数据
    title_img = Image.open(TEXTURED / "title_bg.png").resize((900, 100))
    title_img_draw = ImageDraw.Draw(title_img)
    title_img_draw.text((50, 30), "黑枪数据", "white", font=l4_font_30)
    easy_paste(img, title_img, (0, 655))

    base_img = Image.open(TEXTURED / "base2.png").resize((800, 140))
    base_draw = ImageDraw.Draw(base_img)
    base_draw.text(
        (40, 20),
        f"黑枪次数: {detail['error']['mistake_shout']}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (40, 80),
        f"击倒队友: {detail['error']['down_friend']}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (440, 20),
        f"杀死队友: {detail['error']['kill_friend']}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (440, 80),
        f"放弃队友: {detail['error']['abandon_friend']}",
        "white",
        font=l4_font_30,
    )
    easy_paste(img, base_img, (40, 770))

    # 其他数据
    title_img = Image.open(TEXTURED / "title_bg.png").resize((900, 100))
    title_img_draw = ImageDraw.Draw(title_img)
    title_img_draw.text((50, 30), "其他数据", "white", font=l4_font_30)
    easy_paste(img, title_img, (0, 930))

    base_img = Image.open(TEXTURED / "base3.png").resize((800, 200))
    base_draw = ImageDraw.Draw(base_img)
    base_draw.text(
        (40, 20),
        f"药丸赠与: {detail['sur']['pills_give']}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (40, 80),
        f"保护队友: {detail['sur']['protect_friend']}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (40, 140),
        f"秒妹数量: {detail['sur']['witch_instantly_kill']}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (440, 20),
        f"拉起队友: {detail['sur']['friend_up']}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (440, 80),
        f"近战刀牛: {detail['sur']['melee_charge']}",
        "white",
        font=l4_font_30,
    )
    base_draw.text(
        (440, 140),
        f"地图完成: {detail['sur']['map_clear']}",
        "white",
        font=l4_font_30,
    )
    easy_paste(img, base_img, (40, 1040))

    # 地图数据
    title_img = Image.open(TEXTURED / "title_bg.png").resize((900, 100))
    title_img_draw = ImageDraw.Draw(title_img)
    title_img_draw.text((50, 30), "地图数据", "white", font=l4_font_30)
    easy_paste(img, title_img, (0, 1260))

    #     msg_out = f"""--用户信息如下--

    # {detail["kill_msg"]}
    # """

    #     info_data = detail['info']
    #     msg_out += f"""姓名：{info_data['name']}
    #     # 头像 f"{info_data['avatar']}
    # 最近游戏时间：{info_data['lasttime']}
    # 游玩时间：{info_data['playtime']}
    # """

    #     detail_data = detail['detail']
    #     msg_out += f"""排名：{detail_data['rank']}
    # 得分：{detail_data['source']}
    # 每分钟得分：{detail_data['avg_source']}
    # 感染者消灭：{detail_data['kills']}
    # 生还者消灭：{detail_data['kills_people']}
    # 爆头：{detail_data['headshots']}
    # 爆头率：{detail_data['avg_headshots']}
    # 游玩地图数量：{detail_data['map_play']}
    # """

    #     errorr = detail['error']
    #     msg_out += f"""
    # --- 黑枪数据 ---
    # 黑枪次数：{errorr['mistake_shout']}
    # 杀死队友次数：{errorr['kill_friend']}
    # 击倒队友次数：{errorr['down_friend']}
    # 放弃队友次数：{errorr['abandon_friend']}
    # 让感染者进安全门次数：{errorr['put_into']}
    # 惊扰Witch次数：{errorr['agitate_witch']}
    # """

    return await convert_img(img)
