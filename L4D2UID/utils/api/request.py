import random
import json as js
from copy import deepcopy
from typing import Any, Dict, List, Union, Literal, Optional, cast

from httpx import AsyncClient
from gsuid_core.logger import logger
from lxml import html

from ..database.models import L4D2User
from .api import (
    ANNERANKAPI
)
from .models import (
    UserInfo,

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
        out_type: Optional[str] = 'json',
        need_tk: bool = True,
    ) -> Union[Dict, str, int]:
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
            if 'out_type' != 'json':
                try:
                    raw_data = resp.text
                except ValueError:
                    logger.error(f"解析 JSON 数据失败: {resp.text}")
                    return 4001
                # parsed_data = parse_html(raw_data)
                # tree = html.fromstring(html_content)
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
                        raw_data = {
                            "result": {"error_code": -999, "data": _raw_data}
                        }
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
            params={
                "type": "coop"
            },
            out_type='html',
        )
        if isinstance(data, int):
            return data
        data = cast(str, data)
        tree: html.HtmlElement = html.fromstring(data)
        tbody_content = tree.xpath('/html/body/div[6]/div/div[4]/div/table/tbody')

        # if tbody_content:
        #     rows = tbody_content[0].xpath('./tr')  # 获取所有 <tr> 元素
        #     for row in rows:
        #         cells = row.xpath('./td/text()')  # 获取每行中的 <td> 文本
        return 1

