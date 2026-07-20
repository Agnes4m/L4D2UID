from typing import Dict

from gsuid_core.data_store import get_res_path
from gsuid_core.utils.plugins_config.gs_config import StringConfig
from gsuid_core.utils.plugins_config.models import GSC, GsStrConfig

CONIFG_DEFAULT: Dict[str, GSC] = {
    "platform": GsStrConfig(
        "58平台",
        "选择数据查询平台：电信anne / 呆呆 / 58",
        "电信anne",
        ["电信anne", "呆呆", "58"],
    ),
}

CONFIG_PATH = get_res_path("L4D2UID") / "config.json"

l4d2_config = StringConfig("L4D2UID", CONFIG_PATH, CONIFG_DEFAULT)
