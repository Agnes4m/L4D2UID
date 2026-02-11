import json as js
import random
from copy import deepcopy
from typing import Any, Dict, List, Union, Literal, Optional, cast
from pathlib import Path

from bs4 import BeautifulSoup
from lxml import html
from httpx import AsyncClient

from gsuid_core.logger import logger

from .api import ANNERANKAPI, ANNEPLAYERAPI, ANNESEARCHAPI, DAIDAIPLAYERAPI
from .models import (
    UserSearch,
    AnnePlayer2,
    AnnePlayerInf,
    AnnePlayerSur,
    AnnePlayerInfo,
    AnnePlayerError,
    AnnePlayerDetail,
    AnnePlayerInfAvg,
)
from ..database.models import L4D2User

kill_class = "card-body worldmap d-flex flex-column justify-content-center text-center"


class L4D2Api:
    ssl_verify = False
    _HEADER: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36"
        "(KHTML, like Gecko) perfectworldarena/1.0.24060811   "
        "Chrome/80.0.3987.163"
        "Electron/8.5.5"
        "Safari/537.36",
    }

    async def get_token(self) -> Optional[List[str]]:
        user_list = await L4D2User.get_all_user()
        if user_list:
            user: L4D2User = random.choice(user_list)
            if user.uid is None:
                raise Exception("No valid uid")
            token = await L4D2User.get_user_cookie_by_uid(user.uid)
            if token is None:
                raise Exception("No valid cookie")
            return [user.uid, token]

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

        if json:
            method = "POST"
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
            if resp.status_code == 404:
                return 404

            # 网页访问
            if out_type != "json":
                try:
                    raw_data = resp.content
                except ValueError:
                    logger.error(f"解析 JSON 数据失败: {resp.text}")
                    return 4001
                return raw_data

            else:
                # json访问
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

    async def get_anne_top(self):
        data = await self._l4_request(
            ANNERANKAPI,
            params={"type": "coop"},
            out_type="html",
        )
        if isinstance(data, int):
            return data
        data = cast(str, data)
        tree: html.HtmlElement = html.fromstring(data)
        tree.xpath("/html/body/div[6]/div/div[4]/div/table/tbody")

        # if tbody_content:
        #     rows = tbody_content[0].xpath('./tr')  # 获取所有 <tr> 元素
        #     for row in rows:
        #         cells = row.xpath('./td/text()')  # 获取每行中的 <td> 文本
        return 1

    async def search_player(self, keyword: str):
        data = await self._l4_request(
            ANNESEARCHAPI,
            data={"search": keyword},
            method="POST",
            out_type="html",
        )
        if isinstance(data, int):
            return data
        if isinstance(data, bytes):
            html_content = data
            soup = BeautifulSoup(html_content, "lxml")
            tbody = soup.find("tbody")
            tr_list = tbody.find_all("tr")
            if not tr_list:
                return 401

            out_list: List[UserSearch] = []

            for tr in tr_list:
                steamid = tr.get("onclick").split("steamid=")[-1].rstrip("'")
                td_list = tr.find_all("td")
                logger.info(td_list)
                search_info = {
                    "rank": td_list[0].text,
                    "name": td_list[1].text,
                    "scoce": td_list[2].text,
                    "play_time": td_list[3].text,
                    "last_time": td_list[4].text,
                    "steamid": steamid,
                }
                out_list.append(cast(UserSearch, search_info))
        else:
            return 401
        return out_list[:5]

    async def play_info(self, steam_id: str):
        data = await self._l4_request(
            ANNEPLAYERAPI,
            params={"steamid": steam_id},
            out_type="html",
        )
        if isinstance(data, int):
            return data
        if isinstance(data, bytes):
            html_content = data
            soup = BeautifulSoup(html_content, "lxml")
            # logger.info(soup)
            # with open("/home/ubuntu/soup.html", "w", encoding="utf-8") as f:
            #     f.write(str(soup))
            # kill
            tkill = soup.find(
                "div",
                class_="content text-center text-md-left",
                style="background-color: #f2f2f2;",
            )
            if tkill is None:
                return 523
            kill_tag = tkill.find(
                "div",
                class_=kill_class,
            )

            if kill_tag is None:
                return 401
            kill_text = kill_tag.get_text(separator=" ", strip=True)
            # logger.info(kill_text)

            # 内容
            tbody = soup.find_all(
                "div",
                class_="container text-left",
            )[1]
            if tbody is None:
                return 401
            tbodyy = tbody.find_all("div", class_="card-deck")
            # logger.info(len(tbodyy))

            # 前面部分
            tbody_tags = []
            for one_tbody in tbodyy:
                tbody_tag = one_tbody.find_all(
                    "div",
                    class_="card rounded-0",
                )
                for tbody_one in tbody_tag:
                    tbody_tags.append(tbody_one)

            # 感染者和生还者部分
            ttbody = tbody.find_all("div", class_="card rounded-0")
            tbody_tags.append(ttbody[-2])
            tbody_tags.append(ttbody[-1])

            # logger.info(len(tbody_tags))

            info_tag = tbody_tags[0]
            detail_tag = tbody_tags[1]
            error_tag = tbody_tags[2]
            inf_avg_tag = tbody_tags[3]
            sur_tag = tbody_tags[4]
            # logger.info(sur_tag)
            inf_tag = tbody_tags[5]

            info_tr = info_tag.select("tr")
            info_dict = {
                "name": info_tr[0].select("td")[1].text.strip(),
                "avatar": info_tr[1].select("td")[1].text.strip(),
                "steamid": info_tr[2].select("td")[1].text.strip(),
                "playtime": info_tr[3].select("td")[1].text.strip(),
                "lasttime": info_tr[4].select("td")[1].text.strip(),
            }
            detail_tag = {
                "rank": detail_tag.select("tr")[0].select("td")[1].text.strip(),
                "source": detail_tag.select("tr")[1].select("td")[1].text.strip(),
                "avg_source": detail_tag.select("tr")[2].select("td")[1].text.strip(),
                "kills": detail_tag.select("tr")[3].select("td")[1].text.strip(),
                "kills_people": detail_tag.select("tr")[4].select("td")[1].text.strip(),
                "headshots": detail_tag.select("tr")[5].select("td")[1].text.strip(),
                "avg_headshots": detail_tag.select("tr")[6].select("td")[1].text.strip(),
                "map_play": detail_tag.select("tr")[7].select("td")[1].text.strip(),
            }
            error_tag = {
                "mistake_shout": error_tag.select("tr")[0].select("td")[1].text.strip(),
                "kill_friend": error_tag.select("tr")[1].select("td")[1].text.strip(),
                "down_friend": error_tag.select("tr")[2].select("td")[1].text.strip(),
                "abandon_friend": error_tag.select("tr")[3].select("td")[1].text.strip(),
                "put_into": error_tag.select("tr")[4].select("td")[1].text.strip(),
                "agitate_witch": error_tag.select("tr")[5].select("td")[1].text.strip(),
            }
            inf_avg_dict = {
                "avg_smoker": inf_avg_tag.select("tr")[0].select("td")[1].text.strip(),
                "avg_boomer": inf_avg_tag.select("tr")[1].select("td")[1].text.strip(),
                "avg_hunter": inf_avg_tag.select("tr")[2].select("td")[1].text.strip(),
                "avg_charger": inf_avg_tag.select("tr")[3].select("td")[1].text.strip(),
                "avg_spitter": inf_avg_tag.select("tr")[4].select("td")[1].text.strip(),
                "avg_jockey": inf_avg_tag.select("tr")[5].select("td")[1].text.strip(),
                "avg_tank": inf_avg_tag.select("tr")[6].select("td")[1].text.strip(),
            }
            # logger.info(sur_tag.select("tr"))
            sur_dict = {
                "map_clear": sur_tag.select("tr")[0].select("td")[1].text.strip(),
                "prefect_into": sur_tag.select("tr")[1].select("td")[1].text.strip(),
                "get_oil": sur_tag.select("tr")[2].select("td")[1].text.strip(),
                "ammo_arrange": sur_tag.select("tr")[3].select("td")[1].text.strip(),
                "adrenaline_give": sur_tag.select("tr")[4].select("td")[1].text.strip(),
                "pills_give": sur_tag.select("tr")[5].select("td")[1].text.strip(),
                "first_aid_give": sur_tag.select("tr")[6].select("td")[1].text.strip(),
                "friend_up": sur_tag.select("tr")[7].select("td")[1].text.strip(),
                "diss_friend": sur_tag.select("tr")[8].select("td")[1].text.strip(),
                "save_friend": sur_tag.select("tr")[9].select("td")[1].text.strip(),
                "protect_friend": sur_tag.select("tr")[10].select("td")[1].text.strip(),
                "pro_from_smoker": sur_tag.select("tr")[11].select("td")[1].text.strip(),
                "pro_from_hunter": sur_tag.select("tr")[12].select("td")[1].text.strip(),
                "pro_from_charger": sur_tag.select("tr")[13].select("td")[1].text.strip(),
                "pro_from_jockey": sur_tag.select("tr")[14].select("td")[1].text.strip(),
                "melee_charge": sur_tag.select("tr")[15].select("td")[1].text.strip(),
                "tank_kill": sur_tag.select("tr")[16].select("td")[1].text.strip(),
                "witch_instantly_kill": sur_tag.select("tr")[17].select("td")[1].text.strip(),
            }
            inf_dict = {
                "sur_ace": inf_tag.select("tr")[0].select("td")[1].text.strip(),
                "sur_down": inf_tag.select("tr")[1].select("td")[1].text.strip(),
                "boommer_hit": inf_tag.select("tr")[2].select("td")[1].text.strip(),
                "hunter_prefect": inf_tag.select("tr")[3].select("td")[1].text.strip(),
                "hunter_success": inf_tag.select("tr")[4].select("td")[1].text.strip(),
                "tank_damage": inf_tag.select("tr")[5].select("td")[1].text.strip(),
                "charger_multiple": inf_tag.select("tr")[6].select("td")[1].text.strip(),
            }
            info_dict = cast(AnnePlayerInfo, info_dict)
            detail_dict = cast(AnnePlayerDetail, detail_tag)
            error_dict = cast(AnnePlayerError, error_tag)
            inf_avg_dict = cast(AnnePlayerInfAvg, inf_avg_dict)
            sur_dict = cast(AnnePlayerSur, sur_dict)
            inf_dict = cast(AnnePlayerInf, inf_dict)

            out_dict = {
                "kill_msg": kill_text if kill_text is not None else "",
                "info": info_dict,
                "detail": detail_dict,
                "inf_avg": inf_avg_dict,
                "sur": sur_dict,
                "inf": inf_dict,
                "error": error_dict,
            }

            return cast(AnnePlayer2, out_dict)

    async def get_daidai_player_info(self, steam_id: str, name: str = ""):
        data = await self._l4_request(
            DAIDAIPLAYERAPI,
            params={"steamid": steam_id},
            out_type="html",
        )
        if isinstance(data, int):
            return data
        if isinstance(data, bytes):
            html_content = data
            html = html_content.decode("utf-8")
            with open(Path(__file__).joinpath("soup.html"), "w", encoding="utf-8") as f:
                f.write(html)
