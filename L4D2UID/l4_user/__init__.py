# from typing import Dict

# from gsuid_core.message_models import Button
from gsuid_core.logger import logger
from gsuid_core.sv import SV, Bot, Event
from gsuid_core.utils.message import send_diff_msg

from ..utils.database.models import L4D2Bind

# from ..utils.error_reply import get_error
# from .add_ck import add_uid, add_token, add_stoken

l4_user_bind = SV("L4D2用户绑定")
l4_add_tk = SV("L4D2添加TK", area="DIRECT")
l4_add_uids = SV("L4D2添加UID", area="DIRECT")
l4_switch_paltform = SV("L4D2切换平台", area="DIRECT")


@l4_user_bind.on_command(
    (
        "绑定uid",
        "绑定UID",
        "绑定",
        "切换uid",
        "切换UID",
        "删除uid",
        "删除UID",
    ),
    block=True,
)
async def send_l4_bind_uid_msg(bot: Bot, ev: Event):
    uid = ev.text.strip()
    logger.info("[l4]正在绑定uid{}".format(uid))
    await bot.logger.info("[L4] 开始执行[绑定/解绑用户信息]")
    qid = ev.user_id
    await bot.logger.info("[L4] [绑定/解绑]UserID: {}".format(qid))
    if "64" in uid:
        # 64位uid
        uid = uid.split("64")[0]

        if uid and not uid.isdigit() or uid and len(uid) != 17:

            return await bot.send(
                "你输入了错误的格式!\n正确的UID是个人资料steam64位id\n可以使用[l4搜索 xxx]查询uid"
            )

        if "绑定" in ev.command:
            if not uid:
                return await bot.send(
                    "该命令需要带上正确的uid!(steam64位id)\n如果不知道, 可以使用[l4搜索 xxx]查询uid"
                )
            data = await L4D2Bind.insert_uid(
                qid, ev.bot_id, uid, ev.group_id, is_digit=False
            )
            return await send_diff_msg(
                bot,
                data,
                {
                    0: f"[L4] 绑定UID{uid}成功！",
                    -1: f"[L4] UID{uid}的位数不正确！",
                    -2: f"[L4] UID{uid}已经绑定过了！",
                    -3: "[L4] 你输入了错误的格式!",
                },
            )
        elif "切换" in ev.command:
            retcode = await L4D2Bind.switch_uid_by_game(qid, ev.bot_id, uid)
            if retcode == 0:
                return await bot.send(f"[L4] 切换UID{uid}成功！")
            else:
                return await bot.send(f"[L4] 尚未绑定该UID{uid}")
        else:
            data = await L4D2Bind.delete_uid(qid, ev.bot_id, uid)
            return await send_diff_msg(
                bot,
                data,
                {
                    0: f"[L4] 删除UID{uid}成功！",
                    -1: f"[L4] 该UID{uid}不在已绑定列表中！",
                },
            )
    else:
        if "绑定" in ev.command:
            if not uid:
                return await bot.send(
                    "该命令需要带上正确的uid!(steam64位id)\n如果不知道, 可以使用[l4搜索 xxx]查询uid"
                )
            data = await L4D2Bind.switch_steam32(
                qid, ev.bot_id, uid,
            )
            return await send_diff_msg(
                bot,
                data,
                {
                    0: f"[L4] 绑定UID{uid}成功！",
                    -1: f"[L4] UID{uid}的位数不正确！",
                    -2: f"[L4] UID{uid}已经绑定过了！",
                    -3: "[L4] 你输入了错误的格式!",
                },
            )
        elif "切换" in ev.command:
            retcode = await L4D2Bind.switch_uid_by_game(qid, ev.bot_id, uid)
            if retcode == 0:
                return await bot.send(f"[L4] 切换UID{uid}成功！")
            else:
                return await bot.send(f"[L4] 尚未绑定该UID{uid}")
        else:
            data = await L4D2Bind.delete_uid(qid, ev.bot_id, uid)
            return await send_diff_msg(
                bot,
                data,
                {
                    0: f"[L4] 删除UID{uid}成功！",
                    -1: f"[L4] 该UID{uid}不在已绑定列表中！",
                },
            )        
