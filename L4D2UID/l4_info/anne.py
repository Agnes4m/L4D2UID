import random
from typing import Union
from pathlib import Path

from PIL import Image, ImageDraw

from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import easy_paste, draw_pic_with_ring

from .pil_utils import load_image, draw_text_row, draw_title_section
from ..utils.l4_api import l4_api
from ..utils.l4_font import l4_font_20, l4_font_26, l4_font_40
from .panel_redesign import create_professional_player_stats
from ..utils.api.models import AnnePlayer2
from ..utils.error_reply import get_error

TEXTURED = Path(__file__).parent / "texture2d" / "anne"


def _prepare_background_image(target_w: int = 900, target_h: int = 1200) -> Image.Image:
    """
    准备背景图片 - 支持裁剪和缩放

    Args:
        target_w: 目标宽度
        target_h: 目标高度

    Returns:
        处理后的背景图片

    Raises:
        FileNotFoundError: 未找到背景图像文件
    """
    bg_path = list((TEXTURED / "bg").glob("*.png"))
    if not bg_path:
        raise FileNotFoundError("没有找到背景图像文件。")

    img = Image.open(random.choice(bg_path))
    w, h = img.size

    # 优先裁剪（保留中间部分），次优缩放
    if w >= target_w and h >= target_h:
        left = max(0, (w - target_w) // 2)
        img = img.crop((left, 0, left + target_w, target_h))
    else:
        img = img.resize((target_w, target_h))

    return img


def _extract_player_stats(detail: AnnePlayer2) -> dict:
    """
    提取玩家统计数据

    Args:
        detail: Anne 电信服玩家详情数据

    Returns:
        处理后的玩家统计字典
    """
    return {
        "source": detail["detail"].get("source", 0),
        "kills": detail["detail"].get("kills", 0),
        "rank": detail["detail"].get("rank", 0),
        "playtime": detail["info"].get("playtime", "--"),
        "avg_headshots": detail["detail"].get("avg_headshots", "0%"),
        "avg_source": detail["detail"].get("avg_source", "0"),
        "mistake_shout": detail["error"].get("mistake_shout", 0),
        "kill_friend": detail["error"].get("kill_friend", 0),
        "down_friend": detail["error"].get("down_friend", 0),
        "abandon_friend": detail["error"].get("abandon_friend", 0),
        "pills_give": detail["sur"].get("pills_give", 0),
        "protect_friend": detail["sur"].get("protect_friend", 0),
        "witch_instantly_kill": detail["sur"].get("witch_instantly_kill", 0),
        "friend_up": detail["sur"].get("friend_up", 0),
        "melee_charge": detail["sur"].get("melee_charge", 0),
        "map_clear": detail["sur"].get("map_clear", 0),
    }


def _draw_player_info_panel(title: Image.Image, detail: AnnePlayer2) -> Image.Image:
    """
    绘制玩家信息面板

    Args:
        title: 标题模板图片
        detail: 玩家详情数据

    Returns:
        绘制完成的信息面板
    """
    title_draw = ImageDraw.Draw(title)
    line = load_image(TEXTURED / "line.png")
    easy_paste(title, line, (30, 20))

    # 绘制玩家信息
    draw_text_row(title_draw, f"昵称：{detail['info']['name']}", 70, 20, l4_font_40, "black")
    draw_text_row(title_draw, f"SteamID：{detail['info']['steamid']}", 30, 80, l4_font_26, "black")
    draw_text_row(title_draw, f"上次在线：{detail['info']['lasttime']}", 30, 140, l4_font_20, "black")

    return title


async def get_anne_search_img(keyword: str) -> str:
    detail = await l4_api.search_player(keyword)

    # logger.info(detail)
    if isinstance(detail, int):
        return get_error(detail)

    search_len = len(detail)
    search_msg: str = f"搜索结果{search_len}个：\n"
    for i in range(min(search_len, 5)):
        search_msg += f"""
{i + 1}、{detail[i]["name"]} | {detail[i]["scoce"]} | {detail[i]["last_time"]}
{detail[i]["steamid"]}"""
    return search_msg


async def get_anne_player_img(keyword: str, head_img: Image.Image) -> Union[str, bytes]:
    detail = await l4_api.play_info(keyword)

    logger.info(detail)
    if isinstance(detail, int):
        return get_error(detail)
    if detail is None:
        return get_error(401)

    return await draw_anne_player_img(detail, head_img)


async def draw_anne_player_img(detail: AnnePlayer2, head_img: Image.Image):
    """
    绘制 Annie 电信服玩家信息图片

    Args:
        detail: 玩家详情数据
        head_img: 玩家头像

    Returns:
        转换后的图片数据

    Raises:
        FileNotFoundError: 缺少必要的资源文件
    """
    if len(detail) == 0:
        return get_error(1001)

    # 1. 准备背景
    img = _prepare_background_image(900, 1200)

    # 2. 绘制顶部标题
    draw_title_section(img, "求生之路-anne电信服查询", 20, TEXTURED / "title_bg.png", l4_font_40, text_pos=(-1, 30))

    # 3. 粘贴玩家头像
    easy_paste(img, head_img.resize((100, 100)), (100, 220), direction="cc")

    # 4. 绘制玩家信息面板
    title = load_image(TEXTURED / "title.png").resize((530, 190))
    title = _draw_player_info_panel(title, detail)
    logger.info(detail["info"]["avatar"])
    easy_paste(img, title, (180, 150))

    # 5. 粘贴 Anne 头像（带环形装饰）
    anne_head = load_image(TEXTURED / "anne_head.jpg").resize((100, 100))
    anne_img = await draw_pic_with_ring(anne_head, 100)
    easy_paste(img, anne_img, (800, 220), direction="cc")

    # 6. 提取和绘制玩家统计数据
    stats = _extract_player_stats(detail)
    img = create_professional_player_stats(img, stats, top_offset=320)

    return await convert_img(img)
