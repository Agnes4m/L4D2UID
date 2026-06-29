import json as js
from copy import deepcopy
from typing import Any, Dict, List, Literal, Optional, Union, cast

from asyncio import sleep

from bs4 import BeautifulSoup
from gsuid_core.logger import logger
from httpx import AsyncClient, ConnectError

from .api import ANNEAWARDSAPI, ANNEPLAYERAPI, ANNESEARCHAPI, ANNESTATISTICSAPI, ANNESTATUSAPI
from .models import (
    AnneAward,
    AnneOnlinePlayer,
    AnnePlayer2,
    AnnePlayerDetail,
    AnnePlayerError,
    AnnePlayerInf,
    AnnePlayerInfAvg,
    AnnePlayerInfo,
    AnnePlayerSur,
    AnneStatistics,
    AnneStatus,
    UserSearch,
)


class L4D2Api:
    ssl_verify = False
    _HEADER: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36"
        "(KHTML, like Gecko) perfectworldarena/1.0.24060811   "
        "Chrome/80.0.3987.163"
        "Electron/8.5.5"
        "Safari/537.36",
    }
    _COOKIE = "ANNEWEB_STEAM=c154aac293df935767611f2b72eae854"

    async def _l4_request(
        self,
        url: str,
        method: Literal["GET", "POST"] = "GET",
        header: Dict[str, str] = _HEADER,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        out_type: Optional[str] = "json",
        need_tk: bool = True,
    ) -> Union[Dict, bytes, int]:
        header = deepcopy(self._HEADER)
        header["Cookie"] = self._COOKIE

        if json:
            method = "POST"
        for attempt in range(3):
            try:
                async with AsyncClient(verify=self.ssl_verify) as client:
                    resp = await client.request(
                        method,
                        url=url,
                        headers=header,
                        params=params,
                        json=json,
                        data=data,
                        timeout=300,
                    )
                break
            except ConnectError as e:
                logger.warning(f"[l4] 请求失败 (第{attempt + 1}/3次): {e}")
                if attempt < 2:
                    await sleep(2)
                else:
                    return -1
        if resp.status_code == 404:
            return 404

        if out_type != "json":
            try:
                raw_data = resp.content
            except ValueError:
                logger.error(f"解析 JSON 数据失败: {resp.text}")
                return 4001
            return raw_data

        else:
            try:
                raw_data = await resp.json()
            except:  # noqa: E722
                logger.error("未知的 Content-Type:")
                _raw_data = resp.text
                try:
                    raw_data = js.loads(_raw_data)
                except:  # noqa: E722
                    raw_data = {"result": {"error_code": -999, "data": _raw_data}}
            try:
                if not raw_data["result"]:
                    return raw_data
            except Exception:
                return raw_data
            if "result" in raw_data and "error_code" in raw_data["result"]:
                return raw_data["result"]["error_code"]
            elif raw_data["code"] != 0:
                return raw_data["code"]
            return raw_data

    async def search_player(self, keyword: str):
        data = await self._l4_request(
            ANNESEARCHAPI,
            params={"q": keyword},
            method="GET",
            out_type="html",
        )
        if isinstance(data, int):
            return data
        if isinstance(data, bytes):
            soup = BeautifulSoup(data, "lxml")
            tbody = soup.find("tbody")
            if tbody is None:
                return 401
            tr_list = tbody.find_all("tr")
            if not tr_list:
                return 401

            out_list: List[UserSearch] = []
            for tr in tr_list:
                td_list = tr.find_all("td")
                if len(td_list) < 4:
                    continue
                name_tag = td_list[0].find("a", class_="player-link")
                name = name_tag.text.strip() if name_tag else td_list[0].text.strip()
                steamid_td = td_list[1].text.strip()
                scoce = td_list[2].text.strip()
                last_time = td_list[3].text.strip()
                search_info = {
                    "rank": "",
                    "name": name,
                    "scoce": scoce,
                    "play_time": "",
                    "last_time": last_time,
                    "steamid": steamid_td,
                }
                out_list.append(cast(UserSearch, search_info))
        else:
            return 401
        return out_list[:5]

    def _parse_panel_list(self, panel) -> dict[str, str]:
        items: dict[str, str] = {}
        for li in panel.find_all("li"):
            name_el = li.find("span", class_="name")
            val_el = li.find("span", class_="v")
            if name_el and val_el:
                items[name_el.text.strip()] = val_el.text.strip()
        return items

    def _panel_by_title(self, panels, keyword: str):
        for p in panels:
            h3 = p.find("h3")
            if h3 and keyword in h3.text.strip():
                return p
        return None

    async def play_info(self, steam_id: str, quarter: str | None = None):
        params = {"steamid": steam_id}
        if quarter:
            params["quarter"] = quarter
        data = await self._l4_request(
            ANNEPLAYERAPI,
            params=params,
            out_type="html",
        )
        if isinstance(data, int):
            return data
        if isinstance(data, bytes):
            soup = BeautifulSoup(data, "lxml")

            is_quarter = quarter is not None
            source_label = "季度积分" if is_quarter else "总积分"
            playtime_label = "季度时长" if is_quarter else "游玩时长"
            kills_label = "季度击杀数" if is_quarter else "总击杀数"

            profile = soup.find("div", class_="profile-header")
            if profile is None:
                return 401
            avatar_img = profile.find("img", class_="player-avatar")
            avatar = avatar_img.get("src", "") if avatar_img else ""
            info_div = profile.find("div", class_="profile-info")
            name = ""
            steamid = ""
            if info_div:
                h2 = info_div.find("h2")
                if h2:
                    name = h2.contents[0].strip() if h2.contents else ""
                    badge = h2.find("span", class_="steamid-badge")
                    if badge:
                        steamid = badge.text.strip()
                meta_source = playtime = lasttime = ""
                for m in info_div.find_all("div", class_="meta-item"):
                    text = m.get_text(strip=True)
                    strong = m.find("strong")
                    val = strong.text.strip() if strong else ""
                    if source_label in text:
                        meta_source = val
                    elif playtime_label in text:
                        playtime = val
                    elif "最后上线" in text:
                        lasttime = text.replace("最后上线:", "").strip()
            else:
                meta_source = playtime = lasttime = ""

            scope_el = soup.find("div", class_="profile-scope-current")
            quarter_scope = scope_el.find("strong").text.strip() if scope_el else ""

            kills = avg_headshots = ppm_val = melee_charge = "0"
            pills_give = adrenaline_give = map_clear = "0"
            grid = soup.find("div", class_="stats-grid")
            if grid:
                for card in grid.find_all("div", class_="stat-card"):
                    label_el = card.find("span", class_="label")
                    val_el = card.find("span", class_="val")
                    if not label_el or not val_el:
                        continue
                    label = label_el.text.strip()
                    val = val_el.text.strip()
                    if kills_label in label:
                        kills = val
                    elif "爆头率" in label:
                        avg_headshots = val
                    elif "PPM" in label or "每分钟积分" in label:
                        ppm_val = val
                    elif "近战击杀" in label:
                        melee_charge = val
                    elif label == "给药次数":
                        pills_give = val
                    elif label == "给针次数":
                        adrenaline_give = val
                    elif "地图通关" in label:
                        map_clear = val

            panels = soup.find_all("div", class_="data-panel")
            penalty = self._panel_by_title(panels, "扣分")
            support = self._panel_by_title(panels, "辅助")
            mistake_shout = kill_friend = down_friend = "0"
            abandon_friend = put_into = agitate_witch = "0"
            if penalty:
                pmap = self._parse_panel_list(penalty)
                mistake_shout = pmap.get("黑枪次数", "0")
                kill_friend = pmap.get("杀死队友", "0")
                down_friend = pmap.get("击倒队友", "0")
                abandon_friend = pmap.get("放弃队友", "0")
                put_into = pmap.get("让感染者进安全门", "0")
                agitate_witch = pmap.get("惊扰 Witch", "0")

            first_aid_give = friend_up = "0"
            save_friend = protect_friend = "0"
            if support:
                smap = self._parse_panel_list(support)
                first_aid_give = smap.get("使用医疗包", "0")
                pills_give = smap.get("给药次数", pills_give)
                adrenaline_give = smap.get("给针次数", adrenaline_give)
                friend_up = smap.get("扶起倒地队友", "0")
                save_friend = smap.get("电击救活队友", "0")
                protect_friend = smap.get("保护队友(普感)", "0")

            info_dict = cast(
                AnnePlayerInfo,
                {
                    "name": name,
                    "avatar": avatar,
                    "steamid": steamid,
                    "playtime": playtime,
                    "lasttime": lasttime,
                    "quarter_scope": quarter_scope,
                },
            )
            detail_dict = cast(
                AnnePlayerDetail,
                {
                    "rank": "N/A",
                    "source": meta_source,
                    "avg_source": ppm_val,
                    "kills": kills,
                    "kills_people": "0",
                    "headshots": "0",
                    "avg_headshots": avg_headshots,
                    "map_play": "0",
                },
            )
            error_dict = cast(
                AnnePlayerError,
                {
                    "mistake_shout": mistake_shout,
                    "kill_friend": kill_friend,
                    "down_friend": down_friend,
                    "abandon_friend": abandon_friend,
                    "put_into": put_into,
                    "agitate_witch": agitate_witch,
                },
            )
            inf_avg_dict = cast(
                AnnePlayerInfAvg,
                {
                    "avg_smoker": 0,
                    "avg_boomer": 0,
                    "avg_hunter": 0,
                    "avg_charger": 0,
                    "avg_spitter": 0,
                    "avg_jockey": 0,
                    "avg_tank": 0,
                },
            )
            sur_dict = cast(
                AnnePlayerSur,
                {
                    "map_clear": map_clear,
                    "prefect_into": "0",
                    "get_oil": "0",
                    "ammo_arrange": "0",
                    "adrenaline_give": adrenaline_give,
                    "pills_give": pills_give,
                    "first_aid_give": first_aid_give,
                    "friend_up": friend_up,
                    "diss_friend": "0",
                    "save_friend": save_friend,
                    "protect_friend": protect_friend,
                    "pro_from_smoker": "0",
                    "pro_from_hunter": "0",
                    "pro_from_charger": "0",
                    "pro_from_jockey": "0",
                    "melee_charge": melee_charge,
                    "tank_kill": "0",
                    "witch_instantly_kill": "0",
                },
            )
            inf_dict = cast(
                AnnePlayerInf,
                {
                    "sur_ace": "0",
                    "sur_down": "0",
                    "boommer_hit": "0",
                    "hunter_prefect": "0",
                    "hunter_success": "0",
                    "tank_damage": "0",
                    "charger_multiple": "0",
                },
            )
            out_dict = {
                "kill_msg": "",
                "info": info_dict,
                "detail": detail_dict,
                "inf_avg": inf_avg_dict,
                "sur": sur_dict,
                "inf": inf_dict,
                "error": error_dict,
            }
            return cast(AnnePlayer2, out_dict)

    async def get_server_status(self) -> Union[AnneStatus, int]:
        data = await self._l4_request(ANNESTATUSAPI, out_type="html")
        if isinstance(data, int):
            return data
        if isinstance(data, bytes):
            soup = BeautifulSoup(data, "lxml")
            gstats = soup.find("div", class_="global-stats")
            if gstats is None:
                return 401
            stats: dict[str, str] = {}
            for card in gstats.find_all("div", class_="gstat"):
                num = card.find("div", class_="num")
                label = card.find("div", class_="label")
                if num and label:
                    stats[label.text.strip()] = num.text.strip()
            return cast(
                AnneStatus,
                {
                    "total_players": stats.get("总玩家数", "0"),
                    "total_kills": stats.get("总击杀数", "0"),
                    "total_headshots": stats.get("总爆头数", "0"),
                    "online_now": stats.get("当前在线", "0"),
                    "today_online": stats.get("今日在线过", "0"),
                    "active_30d": stats.get("30天内活跃", "0"),
                },
            )
        return 401

    async def get_online_players(self) -> Union[List[AnneOnlinePlayer], int]:
        data = await self._l4_request(ANNESTATUSAPI, out_type="html")
        if isinstance(data, int):
            return data
        if isinstance(data, bytes):
            soup = BeautifulSoup(data, "lxml")
            tbody = soup.find("tbody")
            if tbody is None:
                return 401
            players: List[AnneOnlinePlayer] = []
            for tr in tbody.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) < 6:
                    continue
                rank = tds[0].text.strip()
                link = tds[1].find("a", class_="player-link")
                name = link.text.strip() if link else tds[1].text.strip()
                steamid = ""
                if link and link.get("href"):
                    from urllib.parse import parse_qs, urlparse

                    qs = parse_qs(urlparse(link["href"]).query)
                    steamid = qs.get("steamid", [""])[0]
                mode = tds[2].text.strip()
                server = tds[3].text.strip()
                score = tds[4].text.strip()
                playtime = tds[5].text.strip()
                players.append(
                    cast(
                        AnneOnlinePlayer,
                        {
                            "rank": rank,
                            "name": name,
                            "steamid": steamid,
                            "mode": mode,
                            "server": server,
                            "score": score,
                            "playtime": playtime,
                        },
                    )
                )
            return players
        return 401

    async def get_awards(self) -> Union[List[AnneAward], int]:
        data = await self._l4_request(ANNEAWARDSAPI, out_type="html")
        if isinstance(data, int):
            return data
        if isinstance(data, bytes):
            soup = BeautifulSoup(data, "lxml")
            import re

            awards: List[AnneAward] = []
            for cat_div in soup.find_all("div", style=re.compile(r"margin:\s*2rem\s+0\s+0\.8rem")):
                category = cat_div.text.strip()
                grid = cat_div.find_next_sibling("div", class_="awards-grid")
                if not grid:
                    continue
                for card in grid.find_all("div", class_="award-card"):
                    icon = card.find("div", class_="award-icon")
                    info = card.find("div", class_="award-info")
                    if not info:
                        continue
                    title = info.find("div", class_="award-title")
                    desc = info.find("div", class_="award-desc")
                    winner_el = info.find("div", class_="winner")
                    winner = steamid = score = ""
                    if winner_el:
                        wlink = winner_el.find("a", class_="winner-name")
                        if wlink:
                            winner = wlink.text.strip()
                            href = wlink.get("href", "")
                            from urllib.parse import parse_qs, urlparse

                            qs = parse_qs(urlparse(href).query)
                            steamid = qs.get("steamid", [""])[0]
                        wval = winner_el.find("div", class_="winner-val")
                        if wval:
                            score = wval.text.strip().replace("成绩:", "").strip()
                    awards.append(
                        cast(
                            AnneAward,
                            {
                                "category": category,
                                "icon": icon.text.strip() if icon else "",
                                "title": title.text.strip() if title else "",
                                "desc": desc.text.strip() if desc else "",
                                "winner": winner,
                                "steamid": steamid,
                                "score": score,
                            },
                        )
                    )
            return awards
        return 401

    async def get_statistics(self, rank_days: int = 30) -> Union[AnneStatistics, int]:
        data = await self._l4_request(ANNESTATISTICSAPI, params={"rank_days": rank_days}, out_type="html")
        if isinstance(data, int):
            return data
        if isinstance(data, bytes):
            soup = BeautifulSoup(data, "lxml")
            boxes = soup.find_all("div", class_="stat-box")
            stats: dict[str, str] = {}
            for box in boxes:
                h3 = box.find("h3")
                val = box.find("div", class_="val")
                if h3 and val:
                    stats[h3.text.strip()] = val.text.strip()

            si_kills: dict[str, str] = {}
            infected = soup.find("div", class_="infected-grid")
            if infected:
                for ibox in infected.find_all("div", class_="infected-box"):
                    name = ibox.find("div", class_="name")
                    val = ibox.find("div", class_="val")
                    if name and val:
                        si_kills[name.text.strip()] = val.text.strip()

            summary: dict[str, str] = {}
            rank_summary = soup.find("div", class_="rank-trend-summary")
            if rank_summary:
                for hm in rank_summary.find_all("div", class_="history-metric"):
                    label = hm.find("div", class_="label")
                    value = hm.find("div", class_="value")
                    if label and value:
                        summary[label.text.strip()] = value.text.strip()

            return cast(
                AnneStatistics,
                {
                    "total_zombie_kills": stats.get("建服以来总击杀丧尸", "0"),
                    "total_headshots": stats.get("全服总爆头数", "0"),
                    "total_melee_kills": stats.get("全服总近战击杀", "0"),
                    "avg_headshot_rate": stats.get("全服平均爆头率", "0%"),
                    "smoker": si_kills.get("Smoker", "0"),
                    "boomer": si_kills.get("Boomer", "0"),
                    "hunter": si_kills.get("Hunter", "0"),
                    "spitter": si_kills.get("Spitter", "0"),
                    "jockey": si_kills.get("Jockey", "0"),
                    "charger": si_kills.get("Charger", "0"),
                    "rank_players": summary.get("玩家数", "0"),
                    "rank_p50": summary.get("中位数", "0"),
                    "rank_p90": summary.get("P90", "0"),
                    "rank_p99": summary.get("P99", "0"),
                    "rank_max": summary.get("最高分", "0"),
                },
            )
        return 401
