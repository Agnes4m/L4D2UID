import datetime
import json
import re
from pathlib import Path
from typing import Union

from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import draw_pic_with_ring, easy_paste
from PIL import Image, ImageDraw

from ..utils.api.models import AnnePlayer2
from ..utils.error_reply import get_error
from ..utils.l4_api import l4_api
from ..utils.l4_font import l4_font_20, l4_font_22, l4_font_26, l4_font_30, l4_font_36
from .panel_redesign import (
    MARGIN_X,
    QUARTER_PANEL_CONFIGS,
    QUARTER_STAT_CARD_CONFIGS,
    create_professional_player_stats,
)
from .pil_utils import Colors, load_image, prepare_bg

TEXTURED = Path(__file__).parent / "texture2d" / "anne"


def _prepare_background_image(target_w: int = 900, target_h: int = 1200) -> Image.Image:
    return prepare_bg(TEXTURED / "bg", target_w, target_h)


def _extract_player_stats(detail: AnnePlayer2) -> dict:
    source_raw = detail["detail"].get("source", 0)
    playtime_str = detail["info"].get("playtime", "--")
    ppm = detail["detail"].get("avg_source", "--")

    if ppm in ("--", "0"):
        try:
            if isinstance(source_raw, str):
                source_num = float(source_raw.replace(",", ""))
            else:
                source_num = float(source_raw)
            if source_num > 0:
                minutes = 0
                m_d = re.search(r"(\d+)天", playtime_str)
                m_h = re.search(r"(\d+)小时", playtime_str)
                m_m = re.search(r"(\d+)分钟", playtime_str)
                if m_d:
                    minutes += int(m_d.group(1)) * 1440
                if m_h:
                    minutes += int(m_h.group(1)) * 60
                if m_m:
                    minutes += int(m_m.group(1))
                if minutes > 0:
                    ppm = f"{source_num / minutes:.2f}"
        except (TypeError, ValueError):
            pass

    return {
        "source": source_raw,
        "kills": detail["detail"].get("kills", 0),
        "rank": detail["detail"].get("rank", 0),
        "ppm": ppm,
        "playtime": playtime_str,
        "avg_headshots": detail["detail"].get("avg_headshots", "0%"),
        "avg_source": detail["detail"].get("avg_source", "0"),
        "mistake_shout": detail["error"].get("mistake_shout", 0),
        "kill_friend": detail["error"].get("kill_friend", 0),
        "down_friend": detail["error"].get("down_friend", 0),
        "abandon_friend": detail["error"].get("abandon_friend", 0),
        "put_into": detail["error"].get("put_into", 0),
        "agitate_witch": detail["error"].get("agitate_witch", 0),
        "pills_give": detail["sur"].get("pills_give", 0),
        "protect_friend": detail["sur"].get("protect_friend", 0),
        "witch_instantly_kill": detail["sur"].get("witch_instantly_kill", 0),
        "friend_up": detail["sur"].get("friend_up", 0),
        "melee_charge": detail["sur"].get("melee_charge", 0),
        "map_clear": detail["sur"].get("map_clear", 0),
        "first_aid_give": detail["sur"].get("first_aid_give", 0),
        "save_friend": detail["sur"].get("save_friend", 0),
        "adrenaline_give": detail["sur"].get("adrenaline_give", 0),
    }


async def get_anne_search_img(keyword: str) -> str:
    detail = await l4_api.search_player(keyword)

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
    now = datetime.datetime.now()
    quarter_id = f"{now.year}{(now.month - 1) // 3 + 1}"
    quarter_label = f"{now.year} Q{(now.month - 1) // 3 + 1}"
    quarter_detail = await l4_api.play_info(keyword, quarter=quarter_id)

    logger.info(f"历史数据: {json.dumps(detail, ensure_ascii=False, default=str)}")
    if quarter_detail and not isinstance(quarter_detail, int):
        logger.info(f"赛季数据: {json.dumps(quarter_detail, ensure_ascii=False, default=str)}")
        qs = quarter_detail["info"].get("quarter_scope", "")
        if qs:
            logger.info(f"赛季标识: {qs}")
            quarter_label = qs
    if isinstance(detail, int):
        return get_error(detail)
    if detail is None:
        return get_error(401)
    if isinstance(quarter_detail, int):
        quarter_detail = None

    return await draw_anne_player_img(detail, head_img, quarter_detail, quarter_label)


async def draw_anne_player_img(
    detail: AnnePlayer2,
    head_img: Image.Image,
    quarter_detail: AnnePlayer2 | None = None,
    quarter_label: str = "",
):
    if len(detail) == 0:
        return get_error(1001)

    img = _prepare_background_image(900, 1600)
    draw = ImageDraw.Draw(img)

    for i in range(3):
        alpha = int(80 * (1 - i / 3))
        y = i * 40
        draw.rectangle([(0, y), (900, y + 40)], fill=(56, 189, 248, alpha))

    draw.text(
        (40, 22),
        "Anne 电信服 · 玩家数据统计",
        font=l4_font_30,
        fill=Colors.TEXT_DARK + (240,),
    )

    card_x, card_y = 40, 100
    card_w, card_h = 820, 230
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=14,
        fill=Colors.PROFESSIONAL_BG + (230,),
        outline=Colors.PROFESSIONAL_BORDER + (120,),
        width=1,
    )

    avatar_resized = head_img.resize((120, 120))
    avatar_ring = await draw_pic_with_ring(avatar_resized, 120)
    easy_paste(img, avatar_ring, (90, card_y + 25), direction="cc")

    info = detail["info"]
    name = info.get("name", "Unknown")
    steamid = info.get("steamid", "")
    playtime = info.get("playtime", "--")
    lasttime = info.get("lasttime", "--")
    score = str(detail["detail"].get("source", "0"))
    total_rank = info.get("total_rank", "")
    total_rank_total = info.get("total_rank_total", "")
    quarter_rank = info.get("quarter_rank", "")
    quarter_rank_total = info.get("quarter_rank_total", "")

    draw.text((170, card_y + 20), name, font=l4_font_36, fill=Colors.TEXT_DARK + (240,))
    draw.text(
        (170, card_y + 60),
        steamid,
        font=l4_font_22,
        fill=Colors.TEXT_LIGHT_GRAY + (200,),
    )

    badge_y = card_y + 100
    badge_text = f"积分 {score}"
    draw.rounded_rectangle(
        [170, badge_y, 350, badge_y + 36],
        radius=18,
        fill=Colors.ACCENT_CYAN + (30,),
        outline=Colors.ACCENT_CYAN + (100,),
        width=1,
    )
    draw.text(
        (180, badge_y + 6),
        badge_text,
        font=l4_font_22,
        fill=(255, 255, 255, 240),
    )

    meta_y = badge_y + 50
    draw.text(
        (170, meta_y + 4),
        f"游玩 {playtime}",
        font=l4_font_22,
        fill=Colors.TEXT_LIGHT_GRAY + (200,),
    )
    draw.text(
        (400, meta_y + 4),
        f"最后上线 {lasttime}",
        font=l4_font_22,
        fill=Colors.TEXT_LIGHT_GRAY + (200,),
    )

    # 排名显示（加大与上方间距）
    rank_parts = []
    if total_rank and total_rank_total:
        rank_parts.append(f"总排名: {total_rank}/{total_rank_total}")
    if quarter_rank and quarter_rank_total:
        rank_parts.append(f"季度排名: {quarter_rank}/{quarter_rank_total}")
    if rank_parts:
        draw.text(
            (170, meta_y + 48),
            "  |  ".join(rank_parts),
            font=l4_font_20,
            fill=Colors.ACCENT_YELLOW + (220,),
        )

    anne_head = load_image(TEXTURED / "anne_head.jpg").resize((80, 80))
    anne_ring = await draw_pic_with_ring(anne_head, 80)
    easy_paste(img, anne_ring, (780, card_y + 45), direction="cc")

    img_w = img.size[0]

    label = f"赛季 {quarter_label}"
    lbox = draw.textbbox((0, 0), label, font=l4_font_26)
    lw = lbox[2] - lbox[0]
    lh = lbox[3] - lbox[1]
    cx = (img_w - lw - 40) // 2
    season_box_y = 325
    draw.rounded_rectangle(
        [cx, season_box_y, cx + lw + 40, season_box_y + lh + 20],
        radius=10,
        fill=Colors.ACCENT_CYAN + (30,),
        outline=Colors.ACCENT_CYAN + (180,),
        width=1,
    )
    draw.text(
        (cx + 20, season_box_y + 9),
        label,
        font=l4_font_26,
        fill=(255, 255, 255, 240),
    )

    season_data_top = season_box_y + lh + 40

    if quarter_detail:
        quarter_stats = _extract_player_stats(quarter_detail)
        img, season_end = create_professional_player_stats(
            img,
            quarter_stats,
            top_offset=season_data_top,
            stat_card_configs=QUARTER_STAT_CARD_CONFIGS,
            panel_configs=QUARTER_PANEL_CONFIGS,
            draw_footer=False,
        )
        draw = ImageDraw.Draw(img)

        hist_label = "历史总数据"
        hbox = draw.textbbox((0, 0), hist_label, font=l4_font_26)
        hw = hbox[2] - hbox[0]
        hh = hbox[3] - hbox[1]
        hcx = (img_w - hw - 40) // 2
        hist_box_y = season_end + 20
        draw.rounded_rectangle(
            [hcx, hist_box_y, hcx + hw + 40, hist_box_y + hh + 20],
            radius=10,
            fill=Colors.ACCENT_CYAN + (30,),
            outline=Colors.ACCENT_CYAN + (180,),
            width=1,
        )
        draw.text(
            (hcx + 20, hist_box_y + 9),
            hist_label,
            font=l4_font_26,
            fill=(255, 255, 255, 240),
        )
        total_top = hist_box_y + hh + 40
    else:
        total_top = season_data_top

    stats = _extract_player_stats(detail)
    img, final_bottom = create_professional_player_stats(
        img,
        stats,
        top_offset=total_top,
        draw_footer=False,
    )
    draw = ImageDraw.Draw(img)

    footer_y = final_bottom + 20
    img_w = img.size[0]
    draw.rounded_rectangle(
        [MARGIN_X, footer_y, img_w - MARGIN_X, footer_y + 40],
        radius=8,
        fill=Colors.PROFESSIONAL_BG + (200,),
        outline=Colors.PROFESSIONAL_BORDER + (80,),
        width=1,
    )
    draw.text(
        (MARGIN_X + 15, footer_y + 10),
        "数据来源: anne.trygek.com",
        font=l4_font_20,
        fill=Colors.TEXT_LIGHT_GRAY + (150,),
    )

    crop_h = min(footer_y + 80, img.size[1])
    img = img.crop((0, 0, img.size[0], crop_h))

    return await convert_img(img)
