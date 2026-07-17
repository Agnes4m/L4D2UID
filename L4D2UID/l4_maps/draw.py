"""地图列表图片渲染 - 使用 PIL 绘制深色风格图片"""

import asyncio
import functools
import io
import random
from pathlib import Path
from typing import List, Optional, Union

from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from PIL import Image, ImageDraw, ImageFont

from ..l4_info.pil_utils import Colors
from ..utils.l4_font import l4_font_16, l4_font_20, l4_font_22, l4_font_30
from .models import GameMap

try:
    import cloudscraper

    _scraper = cloudscraper.create_scraper()
except ImportError:
    _scraper = None
    logger.warning("[l4_maps] cloudscraper 未安装，无法下载缩略图")


async def _download_thumb(url: str) -> Optional[Image.Image]:
    """使用 cloudscraper 下载缩略图（gamemaps.com 需要绕过 Cloudflare）"""
    if not url or _scraper is None:
        return None
    try:
        func = functools.partial(_scraper.get, url, timeout=15)
        resp = await asyncio.get_event_loop().run_in_executor(None, func)
        if resp.status_code == 200:
            return Image.open(io.BytesIO(resp.content)).convert("RGBA")
        logger.warning(f"[l4_maps] 缩略图下载失败: status={resp.status_code}")
    except Exception as e:
        logger.warning(f"[l4_maps] 缩略图下载异常: {e}")
    return None

TEXTURED = Path(__file__).parent.parent / "l4_info" / "texture2d" / "anne"
MARGIN_X = 40

# 地图卡片尺寸
CARD_W = 280
CARD_H = 380
CARD_GAP = 20
CARDS_PER_ROW = 3

# 颜色方案
MAP_COLORS = [
    (56, 189, 248),   # 蓝色
    (52, 211, 153),   # 绿色
    (167, 139, 250),  # 紫色
    (251, 113, 133),  # 红色
    (250, 204, 21),   # 黄色
    (45, 212, 191),   # 青色
]


def _prepare_bg(w: int = 960, h: int = 1200) -> Image.Image:
    """创建深色背景"""
    bg_files = list((TEXTURED / "bg").glob("*.png"))
    if bg_files:
        bg_img = Image.open(random.choice(bg_files))
        bg_img = bg_img.resize((w, h))
    else:
        bg_img = Image.new("RGBA", (w, h), (10, 14, 23))
    overlay = Image.new("RGBA", bg_img.size, (10, 14, 23, 210))
    return Image.alpha_composite(bg_img.convert("RGBA"), overlay)


def _draw_header(draw: ImageDraw.ImageDraw, title: str):
    """绘制页面标题栏"""
    for i in range(3):
        draw.rectangle(
            [(0, i * 40), (960, i * 40 + 40)],
            fill=(56, 189, 248, int(80 * (1 - i / 3))),
        )
    draw.text((40, 22), title, font=l4_font_30, fill=Colors.TEXT_DARK + (240,))


def _draw_footer(draw: ImageDraw.ImageDraw, y: int):
    """绘制底部信息"""
    draw.rounded_rectangle(
        [MARGIN_X, y, 960 - MARGIN_X, y + 40],
        radius=8,
        fill=Colors.PROFESSIONAL_BG + (200,),
        outline=Colors.PROFESSIONAL_BORDER + (80,),
        width=1,
    )
    draw.text(
        (MARGIN_X + 15, y + 10),
        "数据来源: gamemaps.com",
        font=l4_font_20,
        fill=Colors.TEXT_LIGHT_GRAY + (150,),
    )


def _truncate_text(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int
) -> str:
    """截断文本以适应最大宽度"""
    if not text:
        return ""
    bbox = draw.textbbox((0, 0), text, font=font)
    if bbox[2] - bbox[0] <= max_w:
        return text
    for i in range(len(text), 0, -1):
        t = text[:i] + "…"
        bbox = draw.textbbox((0, 0), t, font=font)
        if bbox[2] - bbox[0] <= max_w:
            return t
    return text[:1] + "…"


async def draw_maps_list(
    maps: List[GameMap], section_title: str = "最新地图"
) -> Union[str, bytes]:
    """绘制地图列表图片"""
    n = len(maps)
    if n == 0:
        return "没有找到相关地图"

    display_n = min(n, 18)  # 最多显示 18 个
    rows = (display_n + CARDS_PER_ROW - 1) // CARDS_PER_ROW
    img_h = max(600, 180 + rows * (CARD_H + CARD_GAP) + 100)

    img = _prepare_bg(960, img_h)
    draw = ImageDraw.Draw(img)

    _draw_header(draw, f"GameMaps · {section_title}")

    cards_y = 100
    img_w = 960

    total_w = CARDS_PER_ROW * CARD_W + (CARDS_PER_ROW - 1) * CARD_GAP
    start_x = (img_w - total_w) // 2

    for idx, gm in enumerate(maps[:18]):  # 最多显示 18 个 (6行x3列)
        col = idx % CARDS_PER_ROW
        row = idx // CARDS_PER_ROW
        cx = start_x + col * (CARD_W + CARD_GAP)
        cy = cards_y + row * (CARD_H + CARD_GAP)

        # 卡片背景
        draw.rounded_rectangle(
            [cx, cy, cx + CARD_W, cy + CARD_H],
            radius=10,
            fill=Colors.PROFESSIONAL_BG + (230,),
            outline=Colors.PROFESSIONAL_BORDER + (100,),
            width=1,
        )

        accent = MAP_COLORS[idx % len(MAP_COLORS)]

        # 顶部彩色条
        draw.rounded_rectangle(
            [cx + 12, cy, cx + CARD_W - 12, cy + 3],
            radius=2,
            fill=accent + (200,),
        )

        # 绘制缩略图区域 (如果可用)
        thumb_y = cy + 15
        if gm["thumb"]:
            thumb_img = await _download_thumb(gm["thumb"])
            if thumb_img:
                thumb_img = thumb_img.resize((CARD_W - 20, 150))
                img.paste(thumb_img, (cx + 10, thumb_y), thumb_img)
            else:
                # 缩略图加载失败，绘制占位框
                draw.rounded_rectangle(
                    [cx + 10, thumb_y, cx + CARD_W - 10, thumb_y + 150],
                    radius=6,
                    fill=(30, 40, 60, 200),
                    outline=accent + (80,),
                    width=1,
                )
                draw.text(
                    (cx + CARD_W // 2 - 30, thumb_y + 60),
                    "无预览图",
                    font=l4_font_20,
                    fill=Colors.TEXT_LIGHT_GRAY + (150,),
                )
        else:
            # 无缩略图占位
            draw.rounded_rectangle(
                [cx + 10, thumb_y, cx + CARD_W - 10, thumb_y + 150],
                radius=6,
                fill=(30, 40, 60, 200),
                outline=accent + (80,),
                width=1,
            )

        # 类型标签（加半透明底色）
        if gm["type_label"]:
            label_text = gm["type_label"]
            lbox = draw.textbbox((0, 0), label_text, font=l4_font_20)
            lw = lbox[2] - lbox[0]
            lh = lbox[3] - lbox[1]
            draw.rounded_rectangle(
                [cx + 12, thumb_y + 3, cx + 16 + lw + 4, thumb_y + 8 + lh],
                radius=4,
                fill=(0, 0, 0, 180),
            )
            draw.text(
                (cx + 14, thumb_y + 5),
                label_text,
                font=l4_font_20,
                fill=accent + (240,),
            )

        # 编号（右上角半透明底色）
        if gm["id"]:
            id_text = f"#{gm['id']}"
            ibox = draw.textbbox((0, 0), id_text, font=l4_font_20)
            iw = ibox[2] - ibox[0]
            ih = ibox[3] - ibox[1]
            draw.rounded_rectangle(
                [cx + CARD_W - 16 - iw - 4, thumb_y + 3, cx + CARD_W - 12, thumb_y + 8 + ih],
                radius=4,
                fill=(0, 0, 0, 180),
            )
            draw.text(
                (cx + CARD_W - 14 - iw, thumb_y + 5),
                id_text,
                font=l4_font_20,
                fill=(200, 200, 200, 240),
            )

        # 状态标签 (Updated / New 等)
        if gm["states"]:
            state_x = cx + 12
            state_y = thumb_y + 38
            for st in gm["states"]:
                st_lower = st.lower()
                if "update" in st_lower:
                    st_color = (234, 179, 8)  # 金色
                elif "new" in st_lower:
                    st_color = (34, 197, 94)  # 绿色
                else:
                    st_color = (148, 163, 184)  # 灰色
                sbox = draw.textbbox((0, 0), st, font=l4_font_16)
                sw = sbox[2] - sbox[0]
                sh = sbox[3] - sbox[1]
                draw.rounded_rectangle(
                    [state_x, state_y, state_x + sw + 6, state_y + sh + 4],
                    radius=3,
                    fill=st_color + (200,),
                )
                draw.text(
                    (state_x + 3, state_y + 1),
                    st,
                    font=l4_font_16,
                    fill=(0, 0, 0, 220),
                )
                state_x += sw + 12

        # 标题
        title_y = thumb_y + 160
        title_text = _truncate_text(draw, gm["title"], l4_font_22, CARD_W - 24)
        draw.text(
            (cx + 12, title_y),
            title_text,
            font=l4_font_22,
            fill=Colors.TEXT_DARK + (240,),
        )

        # 作者
        author_y = title_y + 28
        author_text = _truncate_text(
            draw, f"作者: {gm['author']}", l4_font_20, CARD_W - 24
        )
        draw.text(
            (cx + 12, author_y),
            author_text,
            font=l4_font_20,
            fill=Colors.TEXT_LIGHT_GRAY + (180,),
        )

        # 评分
        rating_y = author_y + 24
        draw.text(
            (cx + 12, rating_y),
            f"评分: {gm['rating']}",
            font=l4_font_20,
            fill=Colors.ACCENT_YELLOW + (200,),
        )

        # 查看数
        views_y = rating_y + 24
        draw.text(
            (cx + 12, views_y),
            f"浏览: {gm['views']}",
            font=l4_font_20,
            fill=Colors.TEXT_LIGHT_GRAY + (180,),
        )

        # 日期
        date_text = gm["date"][:10] if gm["date"] else ""
        if date_text:
            draw.text(
                (cx + 12, views_y + 24),
                date_text,
                font=l4_font_20,
                fill=Colors.TEXT_LIGHT_GRAY + (140,),
            )

    # 底部
    final_y = cards_y + rows * (CARD_H + CARD_GAP) + 20
    _draw_footer(draw, final_y)

    crop_h = min(final_y + 80, img.size[1])
    img = img.crop((0, 0, img.size[0], crop_h))
    return await convert_img(img)


async def draw_map_detail(detail) -> Union[str, bytes]:
    """绘制地图详情图片"""
    from .models import MapDetail

    if isinstance(detail, int):
        return f"获取地图详情失败 (错误码: {detail})"

    d: MapDetail = detail

    # ── 预计算高度（留足余量） ──
    desc_len = min(len(d.get("description", "")), 500)
    desc_lines = desc_len // 50 + 2 if desc_len else 0
    has_ss = 1 if d.get("screenshots") else 0
    est_h = 500 + desc_lines * 24 + has_ss * 150 + 100
    img = _prepare_bg(960, max(900, est_h))
    draw = ImageDraw.Draw(img)

    _draw_header(draw, "地图详情")

    x = MARGIN_X
    y = 100
    max_w = 960 - 2 * x  # 880px

    # ══════════════════════════════════════════
    # 1. 类型标签
    # ══════════════════════════════════════════
    tl = d.get("type_label", "")
    if tl:
        draw.rounded_rectangle(
            [x, y, x + 90, y + 28], radius=4, fill=(56, 189, 248, 200),
        )
        draw.text((x + 6, y + 3), tl, font=l4_font_20, fill=(255, 255, 255, 240))
        y += 44

    # ══════════════════════════════════════════
    # 2. 标题
    # ══════════════════════════════════════════
    draw.text((x, y), d["title"], font=l4_font_30, fill=Colors.ACCENT_CYAN + (240,))
    y += 44

    # ══════════════════════════════════════════
    # 3. 编号 + 作者（同行）
    # ══════════════════════════════════════════
    id_text = f"#{d['id']}"
    author = d.get("author", "")
    if author:
        line = f"{id_text}   |   作者: {author}"
    else:
        line = id_text
    draw.text((x, y), line, font=l4_font_20, fill=Colors.TEXT_LIGHT_GRAY + (180,))
    y += 36

    # ══════════════════════════════════════════
    # 4. 统计行
    # ══════════════════════════════════════════
    parts = []
    if d.get("views"):
        parts.append(f"浏览: {d['views']}")
    if d.get("reviews_count"):
        parts.append(f"评价: {d['reviews_count']}")
    if d.get("awards_count"):
        parts.append(f"获奖: {d['awards_count']}")
    if d.get("platform"):
        parts.append(f"平台: {d['platform']}")
    if d.get("file_size"):
        parts.append(f"大小: {d['file_size']}")
    if d.get("version"):
        parts.append(f"版本: {d['version']}")

    if parts:
        sep = "  |  "
        # 分行
        rows_list: list[list[str]] = [[]]
        cur_w = 0
        for p in parts:
            pw = draw.textbbox((0, 0), p, font=l4_font_20)[2]
            gap = sep if len(rows_list[-1]) > 0 else ""
            gw = draw.textbbox((0, 0), gap, font=l4_font_20)[2]
            if cur_w + gw + pw > max_w:
                rows_list.append([p])
                cur_w = pw
            else:
                rows_list[-1].append(p)
                cur_w += gw + pw

        box_h = 38 + (len(rows_list) - 1) * 24
        draw.rounded_rectangle(
            [x, y, 960 - x, y + box_h],
            radius=6,
            fill=Colors.PROFESSIONAL_BG + (200,),
            outline=Colors.PROFESSIONAL_BORDER + (80,),
            width=1,
        )
        for ri, row_parts in enumerate(rows_list):
            row_text = sep.join(row_parts)
            draw.text(
                (x + 12, y + 8 + ri * 24),
                row_text,
                font=l4_font_20,
                fill=Colors.TEXT_LIGHT_GRAY + (220,),
            )
        y += box_h + 16

    # ══════════════════════════════════════════
    # 5. 截图（1行4张）
    # ══════════════════════════════════════════
    screenshots = d.get("screenshots", [])
    if screenshots:
        draw.text((x, y), "截图:", font=l4_font_20, fill=Colors.ACCENT_CYAN + (200,))
        y += 30
        ss_w = 210
        ss_h = 120
        ss_gap = 10
        for idx, ss_url in enumerate(screenshots[:4]):
            sx = x + idx * (ss_w + ss_gap)
            sy = y
            ss_img = await _download_thumb(ss_url)
            if ss_img:
                ss_img = ss_img.resize((ss_w, ss_h))
                img.paste(ss_img, (sx, sy), ss_img)
            else:
                draw.rounded_rectangle(
                    [sx, sy, sx + ss_w, sy + ss_h],
                    radius=4, fill=(30, 40, 60, 200),
                    outline=Colors.PROFESSIONAL_BORDER + (80,), width=1,
                )
                draw.text((sx + ss_w // 2 - 28, sy + ss_h // 2 - 10),
                          "无预览", font=l4_font_16,
                          fill=Colors.TEXT_LIGHT_GRAY + (120,))
        y += ss_h + 20

    # ══════════════════════════════════════════
    # 6. 描述（前500字）
    # ══════════════════════════════════════════
    desc = d.get("description", "")
    if desc:
        draw.text((x, y), "描述:", font=l4_font_20, fill=Colors.ACCENT_CYAN + (200,))
        y += 28
        short = desc[:500]
        cpl = 50
        for i in range(0, len(short), cpl):
            line = short[i:i + cpl]
            draw.text((x + 8, y), line, font=l4_font_16,
                      fill=Colors.TEXT_LIGHT_GRAY + (180,))
            y += 22
            if y > 1050:
                break
        y += 10

    # ══════════════════════════════════════════
    # 7. 标签（自动换行）
    # ══════════════════════════════════════════
    tags = d.get("tags", [])
    if tags:
        all_tags = "  ".join(tags)
        draw.text((x, y), "标签:", font=l4_font_20, fill=Colors.ACCENT_CYAN + (180,))
        y += 26
        tpl = 60
        for i in range(0, len(all_tags), tpl):
            chunk = all_tags[i:i + tpl]
            draw.text((x + 8, y), chunk, font=l4_font_16,
                      fill=Colors.TEXT_LIGHT_GRAY + (160,))
            y += 20
            if y > 1100:
                break
        y += 8

    # ══════════════════════════════════════════
    # 8. 文件信息
    # ══════════════════════════════════════════
    info_bits = []
    if d.get("file_name"):
        info_bits.append(d["file_name"])
    if d.get("file_date"):
        info_bits.append(d["file_date"])
    if info_bits:
        draw.text((x, y), "  |  ".join(info_bits[:3]), font=l4_font_16,
                  fill=Colors.TEXT_LIGHT_GRAY + (140,))
        y += 30

    # ══════════════════════════════════════════
    # 9. 底部
    # ══════════════════════════════════════════
    _draw_footer(draw, max(y + 10, 780))
    crop_h = min(y + 70, img.size[1])
    img = img.crop((0, 0, img.size[0], crop_h))
    return await convert_img(img)
