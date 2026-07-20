from typing import Dict

from gsuid_core.data_store import get_res_path
from gsuid_core.utils.plugins_config.gs_config import StringConfig
from gsuid_core.utils.plugins_config.models import GSC, GsIntConfig, GsStrConfig

CONIFG_DEFAULT: Dict[str, GSC] = {
    "platform": GsStrConfig(
        "58平台",
        "选择数据查询平台：电信anne / 呆呆 / 58",
        "电信anne",
        ["电信anne", "呆呆", "58"],
    ),
    "chat_default_count": GsIntConfig(
        "聊天默认条数",
        "l4聊天 不带数量参数时返回的条数",
        50,
        max_value=200,
    ),
    "chat_default_server": GsStrConfig(
        "聊天默认服务器",
        "l4聊天 不指定服务器时的默认服务器（留空为全部）",
        "",
    ),
}

CONFIG_PATH = get_res_path("L4D2UID") / "config.json"

l4d2_config = StringConfig("L4D2UID", CONFIG_PATH, CONIFG_DEFAULT)
