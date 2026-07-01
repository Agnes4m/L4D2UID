from typing import Dict, List, Union

from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from PIL import Image, ImageDraw

from ..utils.api.models import Player58Response
from ..utils.error_reply import get_error
from ..utils.l4_api import l4_api
from ..utils.l4_font import l4_font_20, l4_font_22, l4_font_24, l4_font_26, l4_font_36

BG = (18, 20, 26)
CARD = (26, 29, 37)
BORDER = (42, 46, 56)
ACCENT = (56, 189, 248)
ACCENT2 = (139, 92, 246)
GREEN = (52, 211, 153)
ORANGE = (251, 146, 60)
RED = (239, 68, 68)
TEXT_WHITE = (240, 240, 240)
TEXT_DIM = (130, 136, 148)
W = 900
MX = 32
CW = W - MX * 2

FONT_TITLE = l4_font_36
FONT_H2 = l4_font_26
FONT_BODY = l4_font_22
FONT_SM = l4_font_20


def rr(draw, x, y, w, h, r=10, fill=CARD, outline=BORDER):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=outline, width=1)


def t(draw, x, y, s, font=FONT_BODY, fill=(200, 205, 215)):
    draw.text((x, y), str(s), font=font, fill=fill)


def tw(draw, s, font=FONT_SM):
    b = draw.textbbox((0, 0), str(s), font=font)
    return b[2] - b[0]


def bar(draw, x, y, w, h, pct, color):
    rr(draw, x, y, w, h, 4, fill=(40, 44, 56))
    if pct > 0:
        rw = max(int(w * pct / 100), 4)
        rr(draw, x, y, rw, h, 4, fill=color)


def _hms(m: int) -> str:
    h, m = divmod(m, 60)
    return f"{h}h{m}m" if h else f"{m}m"


def _pct(a: int, b: int) -> str:
    return f"{round(a / b * 100, 1)}%" if b > 0 else "0%"


_weapon_cats: Dict[str, List[str]] = {
    "霰弹": ["pumpshotgun", "autoshotgun", "shotgun_chrome", "shotgun_spas"],
    "步枪": ["rifle", "rifle_desert", "rifle_ak47", "rifle_sg552", "rifle_m60"],
    "狙击": ["hunting_rifle", "sniper_military", "sniper_awp", "sniper_scout"],
    "SMG": ["smg", "smg_silenced", "smg_mp5"],
    "手枪": ["pistol", "pistol_magnum"],
    "近战": ["knife"],
}


def _weapon_table(v2: dict) -> List[tuple]:
    rows: List[tuple] = []
    for cat, keys in _weapon_cats.items():
        kill = ci = shots = 0
        for k in keys:
            kill += v2.get(f"{k}_kill", 0) or 0
            ci += v2.get(f"{k}_ci_kill", 0) or 0
            shots += v2.get(f"{k}_shots", 0) or 0
        if kill + ci > 0:
            rows.append((cat, kill, ci, shots))
    return rows


async def get_api58_player_img(steam_id: str) -> Union[str, bytes]:
    detail = await l4_api.play_info_58(steam_id)
    if isinstance(detail, int):
        return get_error(detail)

    v5 = detail.get("v5") or {}
    v7 = detail.get("v7") or {}
    v2 = detail.get("v2") or {}
    logger.info(f"[l4]58服数据: v5={len(v5)} v7={len(v7)} v2={len(v2)}")

    name = v5.get("steamname") or v5.get("nickname", "未知")
    steamid = v5.get("steamid", "")
    group = v5.get("user_group", "")
    first = (v5.get("first_time") or "")[:10]
    last = (v5.get("last_time") or "")[:10]
    played = v7.get("played_minutes", 0) or 0
    exp_val = v7.get("exp", 0) or 0

    ci_kill = v7.get("ci_kill", 0) or 0
    ci_hs = v7.get("ci_headshot", 0) or 0
    rounds = v7.get("round", 0) or 0
    wins = v7.get("win", 0) or 0
    damage = v7.get("damage", 0) or 0
    kill_friend = v7.get("kill_friend", 0) or 0
    down_friend = v7.get("down_friend", 0) or 0

    si_total = sum(
        v7.get(k, 0) or 0
        for k in ("smoker_kill", "boomer_kill", "hunter_kill", "spitter_kill", "jockey_kill", "charger_kill")
    )

    tank_val = v7.get("dmg_tank_value", 0) or 0
    tank_total = v7.get("dmg_tank_total", 0) or 0
    witch_val = v7.get("dmg_witch_value", 0) or 0
    witch_total = v7.get("dmg_witch_total", 0) or 0

    si_list = [
        ("Smoker", v7.get("smoker_kill", 0) or 0),
        ("Boomer", v7.get("boomer_kill", 0) or 0),
        ("Hunter", v7.get("hunter_kill", 0) or 0),
        ("Spitter", v7.get("spitter_kill", 0) or 0),
        ("Jockey", v7.get("jockey_kill", 0) or 0),
        ("Charger", v7.get("charger_kill", 0) or 0),
    ]

    scores = [
        ("SI击杀得分", v7.get("score_si_kill", 0) or 0),
        ("CI击杀得分", v7.get("score_ci_kill", 0) or 0),
        ("清道得分", v7.get("score_clear", 0) or 0),
        ("救援得分", v7.get("score_revive", 0) or 0),
        ("保护得分", v7.get("score_protect", 0) or 0),
        ("助攻得分", v7.get("score_assist", 0) or 0),
    ]

    weapons = _weapon_table(v2)
    max_wep = max((k + ci for _, k, ci, _ in weapons), default=0)

    # ── height estimate ──
    box_h = [160, 0, 0]  # box1, box2, box3
    # box2: top(46) + left col(3*48 + 12 + 6*28) + padding(20)
    box_h[1] = 46 + max(6 * 48 + 12 + 3 * 48, 24 + 6 * 26 + 12 + 24 + 3 * 26) + 20
    box_h[2] = 46 + len(weapons) * 32 + 20 if weapons else 0

    img = Image.new("RGB", (W, int(100 + sum(box_h) + 3 * 16 + 40)), BG)
    draw = ImageDraw.Draw(img)

    # header
    for i in range(4):
        a = int(55 * (1 - i / 4))
        draw.rectangle([(0, i * 30), (W, i * 30 + 30)], fill=(ACCENT[0], ACCENT[1], ACCENT[2], a))
    t(draw, MX, 28, "58服 · 玩家数据", FONT_TITLE, (235, 240, 245))

    # ═══ Box 1: 基本信息 ═══
    y = 74
    rr(draw, MX, y, CW, box_h[0], 12)
    t(draw, MX + 20, y + 12, "基本信息", FONT_H2, ACCENT)
    t(draw, MX + 24, y + 44, name, FONT_H2, TEXT_WHITE)
    if group:
        gx = MX + 24 + tw(draw, name, FONT_H2) + 12
        gw = tw(draw, group, FONT_SM) + 14
        rr(draw, gx, y + 46, gw, 24, 12, fill=(ACCENT + (30,)), outline=ACCENT)
        t(draw, gx + 7, y + 49, group, FONT_SM, ACCENT)
    t(draw, MX + 24, y + 76, f"SteamID: {steamid}", FONT_SM, TEXT_DIM)
    t(draw, MX + 24, y + 100, f"首次 {first}", FONT_SM, TEXT_DIM)
    t(draw, MX + 24, y + 124, f"最后 {last}", FONT_SM, TEXT_DIM)
    t(draw, MX + 320, y + 76, f"时长 {_hms(played)}", FONT_SM, TEXT_DIM)
    t(draw, MX + 320, y + 100, f"EXP {exp_val}", FONT_SM, TEXT_DIM)
    y += box_h[0] + 16

    # ═══ Box 2: 击杀信息 ═══
    rr(draw, MX, y, CW, box_h[1], 12)
    t(draw, MX + 20, y + 12, "击杀信息", FONT_H2, ACCENT)
    by = y + 46

    # left col
    left_w = int(CW * 0.55)
    right_w = CW - left_w - 16

    stats_main = [
        ("步枪击杀", ci_kill, ACCENT),
        ("爆头率", _pct(ci_hs, ci_kill), GREEN),
        ("特感击杀", si_total, ACCENT2),
        ("胜率", _pct(wins, rounds), GREEN),
        ("局数", rounds, ORANGE),
        ("胜场", wins, ORANGE),
    ]

    stats_more = [
        ("坦克伤害", f"{tank_val}/{tank_total}"),
        ("Witch伤害", f"{witch_val}/{witch_total}"),
        ("总伤害", damage),
    ]

    for i, (lbl, val, clr) in enumerate(stats_main):
        sx = MX + 20
        sy = by + i * 48
        t(draw, sx, sy, lbl, FONT_SM, TEXT_DIM)
        t(draw, sx + 120, sy, str(val), FONT_BODY, clr)
        if i < 4:
            pct = 0
            if i == 0:
                pct = min(ci_kill / max(ci_kill + si_total, 1) * 100, 100)
            elif i == 1:
                pct = round(ci_hs / max(ci_kill, 1) * 100, 1)
            elif i == 2:
                pct = min(si_total / max(ci_kill + si_total, 1) * 100, 100)
            elif i == 3:
                pct = round(wins / max(rounds, 1) * 100, 1)
            bar(draw, sx + 120, sy + 26, 150, 6, pct, clr)

    more_y = by + len(stats_main) * 48 + 12
    for i, (lbl, val) in enumerate(stats_more):
        sx = MX + 20
        sy = more_y + i * 48
        t(draw, sx, sy, lbl, FONT_SM, TEXT_DIM)
        t(draw, sx + 120, sy, str(val), FONT_BODY, (GREEN if "坦克" in lbl else TEXT_WHITE))
        pct = 0
        if "坦克" in lbl:
            pct = round(tank_val / max(tank_total, 1) * 100, 1)
        elif "Witch" in lbl:
            pct = round(witch_val / max(witch_total, 1) * 100, 1)
        if pct > 0:
            bar(draw, sx + 120, sy + 26, 150, 6, pct, (GREEN if "坦克" in lbl else ORANGE))

    # right col
    sx = MX + 20 + left_w + 16
    t(draw, sx, by, "特感明细", FONT_SM, ACCENT2)
    for i, (lbl, val) in enumerate(si_list):
        siy = by + 24 + i * 26
        t(draw, sx + 8, siy, lbl, FONT_SM, TEXT_DIM)
        t(draw, sx + 100, siy, str(val), FONT_SM, TEXT_WHITE)

    sc_y = by + len(si_list) * 26 + 12
    t(draw, sx, sc_y, "评分", FONT_SM, ACCENT2)
    for i, (lbl, val) in enumerate(scores):
        row = i // 2
        col = i % 2
        tx = sx + 8 + col * (right_w // 2)
        t(draw, tx, sc_y + 24 + row * 26, lbl, FONT_SM, TEXT_DIM)
        t(draw, tx + 80, sc_y + 24 + row * 26, f"{val:.1f}", FONT_SM, TEXT_WHITE)

    y += box_h[1] + 16

    # ═══ Box 3: 武器信息 ═══
    if weapons:
        rr(draw, MX, y, CW, box_h[2], 12)
        t(draw, MX + 20, y + 12, "武器信息", FONT_H2, ACCENT)
        hx = MX + 20
        t(draw, hx, y + 46, "类别", FONT_SM, ACCENT)
        t(draw, hx + 120, y + 46, "特感击杀", FONT_SM, ACCENT)
        t(draw, hx + 240, y + 46, "小丧尸", FONT_SM, ACCENT)
        t(draw, hx + 340, y + 46, "射击数", FONT_SM, ACCENT)
        for i, (cat, kill, ci, shots) in enumerate(weapons):
            wy = y + 70 + i * 32
            total = kill + ci
            pct = total / max_wep * 100 if max_wep > 0 else 0
            bar(draw, hx + 440, wy + 6, 200, 6, pct, ACCENT)
            t(draw, hx, wy, cat, FONT_BODY, TEXT_WHITE)
            t(draw, hx + 120, wy, str(kill), FONT_SM, TEXT_DIM)
            t(draw, hx + 240, wy, str(ci), FONT_SM, TEXT_DIM)
            t(draw, hx + 340, wy, str(shots), FONT_SM, TEXT_DIM)
        y += box_h[2] + 16

    img = img.crop((0, 0, W, y + 20))
    return await convert_img(img)
