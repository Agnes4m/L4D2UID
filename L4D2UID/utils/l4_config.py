from typing import Dict

from gsuid_core.data_store import get_res_path

from gsuid_core.utils.plugins_config.gs_config import StringConfig
from gsuid_core.utils.plugins_config.models import GSC

CONIFG_DEFAULT: Dict[str, GSC] = {}

CONFIG_PATH = get_res_path("L4D2UID") / "config.json"

l4d2_config = StringConfig("L4D2UID", CONFIG_PATH, CONIFG_DEFAULT)
