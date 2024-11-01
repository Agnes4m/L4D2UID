# coding:utf-8
import json
from typing import cast

from gsuid_core.bot import Bot
from gsuid_core.data_store import get_res_path
from gsuid_core.models import Event
from gsuid_core.plugins.L4D2UID.L4D2UID.l4_info.anne import get_anne_search_img
from gsuid_core.sv import SV
from ..utils.database.models import L4D2Bind
from gsuid_core.utils.database.api import get_uid
from loguru import logger

l4_user_info = SV("L4D2用户信息查询")


@l4_user_info.on_command(("查询"), block=True)
async def send_l4_info_msg(bot: Bot, ev: Event):

    arg = ev.text.strip()
    
    # 判断服务器类型
    if "云" in arg:
        tag = "云"
        arg = arg.replace("云", "")
    elif "呆呆" in arg:
        tag = "呆呆"
        arg = arg.replace("呆呆", "")
    else:
        tag = await L4D2Bind.get_searchtype(ev.user_id)
    if tag is None:
        tag = "云"
    uid64 = await get_uid(bot, ev, L4D2Bind)
    if uid64 is None:
        return await bot.send("未绑定uid")
    if tag == "云":
        out_msg =await get_anne_search_img(uid64)

        await bot.send(out_msg)
