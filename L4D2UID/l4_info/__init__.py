# coding:utf-8
"""
L4D2 查询模块 - 信息查询入口

集成 Anne 电信服和呆呆服两个服务器的玩家查询功能
提供查询和搜索指令
"""

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.image_tools import get_avatar_with_ring

from .anne import get_anne_player_img, get_anne_search_img
from .daidai import get_daidai_player_img
from ..utils.error_reply import get_error
from ..utils.database.models import L4D2Bind

l4_user_info = SV("L4D2用户信息查询")


@l4_user_info.on_command(("查询"), block=True)
async def send_l4_info_msg(bot: Bot, ev: Event):
    arg = ev.text.strip()
    if ev.at:
        user_id = ev.at
    else:
        user_id = ev.user_id

    # 判断服务器类型
    tag = await L4D2Bind.get_searchtype(user_id)
    logger.info(f"[l4]查询服务器{tag}用户{user_id}")
    if tag is None or not tag:
        tag = "云"

    logger.info(f"[l4]正在查询服务器{tag}")

    if tag == "云":
        uid32 = await L4D2Bind.get_steam32(user_id)
        if uid32 is None:
            return await bot.send(get_error(302))

        if arg:
            uid32 = arg

        logger.info(f"[l4]服务器{tag}的uid32为{uid32}")
        out_msg = await get_anne_player_img(uid32, await get_avatar_with_ring(ev))
        await bot.send(out_msg)

    elif tag == "呆呆":
        uid32 = await L4D2Bind.get_steam32(user_id)
        user_name = await L4D2Bind.get_name(user_id)
        logger.info(f"[l4]服务器{tag}的uid32为{uid32}")

        if not arg:
            if uid32:
                arg = uid32
            elif user_name:
                arg = user_name
            else:
                return await bot.send(get_error(-51))

        out_msg = await get_daidai_player_img(arg)
        await bot.send(out_msg)
    else:
        return await bot.send(get_error(501))


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
