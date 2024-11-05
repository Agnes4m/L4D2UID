


from os import error
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

    logger.info(detail)
    if isinstance(detail, int):
        return get_error(detail)
    if detail is None:
        return get_error(401)

    return await draw_anne_player_img(detail)

async def draw_anne_player_img(detail: AnnePlayer2):
    if not detail:
        return get_error(1001)
    
    msg_out = f"""--用户信息如下--

{detail["kill_msg"]}
"""
        
    info_data = detail['info']
    msg_out += f"""姓名：{info_data['name']}
    # 头像 f"{info_data['avatar']}
最近游戏时间：{info_data['lasttime']}
游玩时间：{info_data['playtime']}
"""
    
    detail_data = detail['detail']
    msg_out += f"""排名：{detail_data['rank']}
得分：{detail_data['source']}
每分钟得分：{detail_data['avg_source']}
感染者消灭：{detail_data['kills']}
生还者消灭：{detail_data['kills_people']}
爆头：{detail_data['headshots']}
爆头率：{detail_data['avg_headshots']}
游玩地图数量：{detail_data['map_play']}
"""
    
    
    errorr = detail['error']
    msg_out += f""" 
--- 黑枪数据 ---
黑枪次数：{errorr['mistake_shout']}
杀死队友次数：{errorr['kill_friend']}
击倒队友次数：{errorr['down_friend']}
放弃队友次数：{errorr['abandon_friend']}
让感染者进安全门次数：{errorr['put_into']}
惊扰Witch次数：{errorr['agitate_witch']}
"""
    

    return await text2pic(msg_out)