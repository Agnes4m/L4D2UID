


import re
from typing import Union, List

from gsuid_core.logger import logger
from ..utils.api.models import AnnePlayer2, UserSearch
from ..utils.l4_api import l4_api
from gsuid_core.utils.image.convert import text2pic
from ..utils.error_reply import get_error


async def get_anne_search_img(keyword: str  ) -> Union[str, bytes]:
    detail = await l4_api.search_player(keyword)

    # logger.info(detail)
    if isinstance(detail, int):
        return get_error(detail)


    return ""

async def get_anne_player_img(keyword: str):
    detail = await l4_api.play_info(keyword)

    # logger.info(detail)
    if isinstance(detail, int):
        return get_error(detail)
    if detail is None:
        return get_error(401)

    return await draw_anne_player_img(detail)

async def draw_anne_player_img(detail: AnnePlayer2):
    if not detail:
        return 1001
    
    msg_out = f"""--用户信息如下--
{detail["kill_msg"]}
"""
        
    info_data = detail['info']
    msg_out += f"姓名：{info_data['name']}\n"
    # 头像 f"{info_data['avatar']}\n"
    msg_out += f"最近游戏时间：{info_data['lasttime']}\n"
    msg_out += f"游玩时间：{info_data['playtime']}\n"
    
    detail_data = detail['detail']
    msg_out += f"排名：{detail_data['rank']}"
    msg_out += f"得分：{detail_data['source']}"
    msg_out += f"每分钟得分：{detail_data['avg_source']}"
        
    return await text2pic(msg_out)