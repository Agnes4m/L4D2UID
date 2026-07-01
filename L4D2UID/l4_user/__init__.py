from gsuid_core.sv import SV, Bot, Event
from gsuid_core.logger import logger
from gsuid_core.utils.message import send_diff_msg

from ..utils.database.models import L4D2Bind
from ..utils.l4_config import l4d2_config
from ..utils.steam_convert import to_steam32

l4_user_bind = SV("L4D2用户绑定")
l4_switch_paltform = SV("L4D2切换平台")
l4_admin = SV("L4D2管理", pm=2)


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
    if not uid:
        return await bot.send("该命令需要带上正确的uid!(steam32位id)\n如果不知道, 可以使用[l4搜索 xxx]查询uid")
    elif not uid.isdigit() and ":" in uid:
        if "绑定" in ev.command:
            if not uid:
                return await bot.send("该命令需要带上正确的uid!(steam64位id)\n如果不知道, 可以使用[l4搜索 xxx]查询uid")
            data = await L4D2Bind.switch_steam32(
                qid,
                ev.bot_id,
                uid,
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
            retcode = await L4D2Bind.switch_steam32(qid, ev.bot_id, uid)
            if retcode == 0:
                return await bot.send(f"[L4] 切换UID{uid}成功！")
            else:
                return await bot.send(f"[L4] 尚未绑定该UID{uid}")

        else:
            retcode = await L4D2Bind.switch_steam32(qid, ev.bot_id, "")
            if retcode == 0:
                return await bot.send(f"[L4] 切换UID{uid}成功！")
            else:
                return await bot.send(f"[L4] 尚未绑定该UID{uid}")

    elif uid.isdigit() and len(uid) == 17:
        if "绑定" in ev.command:
            if not uid:
                return await bot.send("该命令需要带上正确的uid!(steam64位id)\n如果不知道, 可以使用[l4搜索 xxx]查询uid")

            data = await L4D2Bind.insert_uid(qid, ev.bot_id, uid, ev.group_id, is_digit=False)
            if data == 0:
                steam32 = to_steam32(uid)
                await L4D2Bind.update_data(qid, ev.bot_id, steam32=steam32)
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
                steam32 = to_steam32(uid)
                await L4D2Bind.update_data(qid, ev.bot_id, steam32=steam32)
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
                return await bot.send("该命令需要带上你的昵称")
            data = await L4D2Bind.switch_name(
                qid,
                ev.bot_id,
                uid,
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
            retcode = await L4D2Bind.switch_name(qid, ev.bot_id, uid)
            if retcode == 0:
                return await bot.send(f"[L4] 切换UID{uid}成功！")
            else:
                return await bot.send(f"[L4] 尚未绑定该UID{uid}")
        else:
            data = await L4D2Bind.delete_data(
                qid,
                ev.bot_id,
            )
            return await send_diff_msg(
                bot,
                data,
                {
                    0: f"[L4] 删除UID{uid}成功！",
                    -1: f"[L4] 该UID{uid}不在已绑定列表中！",
                },
            )


@l4_user_bind.on_command(
    ("切换"),
    block=True,
)
async def send_l4_switch_paltform_msg(bot: Bot, ev: Event):
    paltform = ev.text.strip()
    logger.info(paltform)
    bot_id = ev.bot_id
    logger.info("[l4] 开始执行[切换平台]")
    qid = ev.user_id
    logger.info("[l4] [切换平台]UserID: {} - {}".format(qid, paltform))

    if "电信" in paltform or "云" in paltform:
        await L4D2Bind.switch_searchtype(qid, bot_id, "云")
        return await bot.send("[l4] 切换电信anne服务器成功！")
    elif "呆" in paltform:
        await L4D2Bind.switch_searchtype(qid, bot_id, "呆呆")
        return await bot.send("[l4] 切换呆呆服务器成功！")
    else:
        return await bot.send("[l4] 平台错误！")


@l4_admin.on_command(
    ("平台设置"),
    block=True,
)
async def send_l4_set_platform_msg(bot: Bot, ev: Event):
    platform = ev.text.strip()
    valid = {"电信anne", "呆呆", "58"}
    if platform not in valid:
        return await bot.send(f"[l4] 无效平台！可选: {'/'.join(valid)}")
    l4d2_config.set_config("platform", platform)
    return await bot.send(f"[l4] 全局平台已切换为: {platform}")
