from gsuid_core.models import Event

from ..utils.database.models import L4D2User


async def add_token(ev: Event, tk: str):
    await L4D2User.insert_data(ev.user_id, ev.bot_id, cookie=tk)
    return "完美token添加成功！"


async def add_stoken(ev: Event, sk: str):
    await L4D2User.insert_data(ev.user_id, ev.bot_id, stoken=sk)
    return "5etoken添加成功！"


async def add_uid(ev: Event, uid: str):
    await L4D2User.insert_data(ev.user_id, ev.bot_id, uid=uid)
    return "添加成功！"
