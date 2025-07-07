from typing import Union

from gsuid_core.bot import Bot
from gsuid_core.logger import logger

UID_HINT = "[l4] 你还没有绑定UID，请先使用[l4绑定]命令进行绑定"
CK_HINT = "[l4] 你还没有添加可用cookie，请先使用[l4添加ck]命令进行绑定"

error_dict = {
    -51: UID_HINT,
    -511: CK_HINT,
    4001: "4001 - 登录已失效，请重新添加sk",
    8000102: "8000102 - auth check failed!\n该tk失效或不正确, 请检查错误tk!",
    500: "请求参数错误,请输入正确的参数",
    501: "存储参数错误,请使用[l4切换]命令更换正确的平台",
    401: "结果为空,请确认是否搜索正确",
    523: "游戏服务器坏掉了，请联系服务器管理员",
    302: "请先绑定UID",
}


def get_error(retcode: Union[int, str]) -> str:
    return error_dict.get(
        int(retcode),
        f"未知错误, 错误码为{retcode}, 可能由于隐私设置不允许搜索!",
    )


not_player = "查无此人"


async def try_send(bot: Bot, msg: Union[str, bytes]):
    try:
        await bot.send(msg)
    except Exception as E:
        logger.error(E)
        no_inter = "网络开小差了呢，图片没发出来，请重发指令试试"
        await bot.send(no_inter)
