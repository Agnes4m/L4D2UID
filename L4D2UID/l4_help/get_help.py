from pathlib import Path
from typing import Dict

import aiofiles
from gsuid_core.help.draw_new_plugin_help import get_new_help
from gsuid_core.help.model import PluginHelp
from gsuid_core.sv import get_plugin_prefix
from msgspec import json as msgjson
from PIL import Image

from ..version import L4D2UID_version

HELP_DATA = Path(__file__).parent / "help.json"
ICON_PATH = Path(__file__).parent / "icon_path"
TEXT_PATH = Path(__file__).parent / "texture2d"
ICON = TEXT_PATH / "icon.png"

PREFIX = get_plugin_prefix("L4D2UID")


def get_footer():
    return Image.open(TEXT_PATH / "footer.png")


async def get_help_data() -> Dict[str, PluginHelp]:
    async with aiofiles.open(HELP_DATA, "rb") as file:
        return msgjson.decode(await file.read(), type=Dict[str, PluginHelp])


async def get_help():
    return await get_new_help(
        plugin_name="L4D2UID",
        plugin_info={f"v{L4D2UID_version}": ""},
        plugin_icon=Image.open(ICON),
        plugin_help=await get_help_data(),
        plugin_prefix=PREFIX,
        help_mode="light",
        banner_bg=Image.open(
            TEXT_PATH / "banner_bg.jpg",
        ),
        banner_sub_text="求生之路2真好玩!",
        help_bg=Image.open(TEXT_PATH / "bg.jpg"),
        cag_bg=Image.open(TEXT_PATH / "cag_bg.png"),
        item_bg=Image.open(TEXT_PATH / "item.png"),
        icon_path=ICON_PATH,
        footer=get_footer(),
        enable_cache=True,
    )
