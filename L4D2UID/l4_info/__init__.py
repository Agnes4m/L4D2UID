# coding:utf-8

import json

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.image.image_tools import get_avatar_with_ring

from ..utils.database.models import L4D2Bind
from ..utils.error_reply import get_error
from ..utils.l4_api import l4_api
from ..utils.l4_config import l4d2_config
from .anne import get_anne_player_img, get_anne_search_img
from .api58 import get_api58_player_img
from .daidai import get_daidai_player_img
from .status import draw_awards_img, draw_server_status_img

l4_user_info = SV("L4D2用户信息查询")


@l4_user_info.on_command(("查询"), block=True)
async def send_l4_info_msg(bot: Bot, ev: Event):
    arg = ev.text.strip()
    if ev.at:
        user_id = ev.at
    else:
        user_id = ev.user_id

    # 先读用户个人 searchtype 覆盖（由 l4切换 设置）
    user_searchtype = await L4D2Bind.get_searchtype(user_id)
    platform = l4d2_config.get_config("platform").data
    if user_searchtype == "呆呆":
        platform = "呆呆"
    elif user_searchtype == "云":
        platform = "电信anne"
    logger.info(f"[l4]平台配置为{platform} (用户searchtype={user_searchtype})")

    if platform == "58":
        uid64 = await L4D2Bind.select_data(user_id)
        uid64 = uid64.uid if uid64 and uid64.uid else None
        if uid64 is None:
            steam32 = await L4D2Bind.get_steam32(user_id)
            if steam32 and ":" in steam32:
                from ..utils.steam_convert import to_steam64

                uid64 = to_steam64(steam32)
            else:
                uid64 = steam32
        if uid64 is None:
            return await bot.send(get_error(302))

        if arg:
            uid64 = arg

        logger.info(f"[l4]58服查询{uid64}")
        out_msg = await get_api58_player_img(uid64)
        return await bot.send(out_msg)

    if platform == "呆呆":
        uid32 = await L4D2Bind.get_steam32(user_id)
        user_name = await L4D2Bind.get_name(user_id)
        logger.info(f"[l4]呆呆服查询{uid32}")

        if not arg:
            if uid32:
                arg = uid32
            elif user_name:
                arg = user_name
            else:
                return await bot.send(get_error(-51))

        out_msg = await get_daidai_player_img(arg)
        return await bot.send(out_msg)

    uid32 = await L4D2Bind.get_steam32(user_id)
    if uid32 is None:
        return await bot.send(get_error(302))

    if arg:
        uid32 = arg

    logger.info(f"[l4]电信anne服查询{uid32}")
    out_msg = await get_anne_player_img(uid32, await get_avatar_with_ring(ev))
    await bot.send(out_msg)


@l4_user_info.on_command(("搜索"), block=True)
async def search_l4_info_msg(bot: Bot, ev: Event):
    arg = ev.text.strip()
    if ev.at:
        user_id = ev.at
    else:
        user_id = ev.user_id
    tag = await L4D2Bind.get_searchtype(user_id)
    if tag is None or not tag:
        tag = "云"
    logger.info(f"[l4]正在搜索服务器{tag}用户")
    if tag == "云":
        search_msg = await get_anne_search_img(arg)
        await bot.send(search_msg)


@l4_user_info.on_command(("状态"), block=True)
async def send_server_status_msg(bot: Bot, ev: Event):
    status = await l4_api.get_server_status()
    if isinstance(status, int):
        return await bot.send(get_error(status))
    players = await l4_api.get_online_players()
    if isinstance(players, int):
        return await bot.send(get_error(players))
    logger.info(f"状态数据: {json.dumps(status, ensure_ascii=False)}")
    logger.info(f"在线玩家: {json.dumps(players[:3], ensure_ascii=False)}")
    out_msg = await draw_server_status_img(status, players)
    await bot.send(out_msg)


@l4_user_info.on_command(("统计"), block=True)
async def send_statistics_msg(bot: Bot, ev: Event):
    awards = await l4_api.get_awards()
    if isinstance(awards, int):
        return await bot.send(get_error(awards))
    logger.info(f"荣誉数据: {json.dumps(awards[:3], ensure_ascii=False)}...")
    out_msg = await draw_awards_img(awards)
    await bot.send(out_msg)
