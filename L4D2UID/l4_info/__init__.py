# coding:utf-8
import json
from typing import cast

from loguru import logger
from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.data_store import get_res_path
from gsuid_core.utils.database.api import get_uid

csgo_user_info = SV("L4D2用户信息查询")


@csgo_user_info.on_command(("查询"), block=True)
async def send_csgo_info_msg(bot: Bot, ev: Event):
    
    arg = ev.text.strip()
    logger.info(arg)
