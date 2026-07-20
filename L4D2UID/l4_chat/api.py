"""Anne 聊天记录 API"""

import asyncio
import functools
from typing import List, Optional, Union

from bs4 import BeautifulSoup
from gsuid_core.logger import logger

from .models import ChatMessage

try:
    import cloudscraper

    _scraper = cloudscraper.create_scraper()
except ImportError:
    _scraper = None
    logger.warning("[l4_chat] cloudscraper 未安装")

CHAT_HOST = "https://anne.trygek.com"
CHAT_URL = f"{CHAT_HOST}/chat/"
ANNEWEB_COOKIE = "ANNEWEB_STEAM=c154aac293df935767611f2b72eae854"


class ChatApi:
    """Anne 聊天记录 API 封装"""

    def __init__(self):
        self._session = None

    def _get_scraper(self):
        return _scraper

    async def _fetch_html(self, url: str) -> Optional[str]:
        scraper = self._get_scraper()
        if scraper is None:
            return None

        for attempt in range(3):
            try:
                func = functools.partial(
                    scraper.get,
                    url,
                    timeout=30,
                    cookies={"ANNEWEB_STEAM": "c154aac293df935767611f2b72eae854"},
                )
                resp = await asyncio.get_event_loop().run_in_executor(None, func)
                if resp.status_code == 200:
                    return resp.text
                logger.warning(f"[l4_chat] 请求失败 (第{attempt + 1}/3次): status={resp.status_code}")
                if attempt < 2:
                    await asyncio.sleep(2)
            except Exception as e:
                logger.warning(f"[l4_chat] 请求异常: {e}")
                if attempt < 2:
                    await asyncio.sleep(2)
        return None

    async def _parse_row(self, tr) -> Optional[ChatMessage]:
        """解析表格行"""
        try:
            tds = tr.find_all("td")
            if len(tds) < 4:
                return None

            # 时间
            time_text = tds[0].get_text(strip=True)

            # 服务器/地图
            server_text = ""
            map_text = ""
            server_div = tds[1].find("div", class_="server-info")
            if server_div:
                # Contains server name and map separated by <br>
                parts = server_div.get_text("\n", strip=True).split("\n")
                if parts:
                    server_text = parts[0]
                if len(parts) > 1:
                    map_text = parts[1].replace("地图：", "").strip()

            # 玩家
            player_name = ""
            steamid = ""
            name_span = tds[2].find("span", class_="player-name")
            if name_span:
                player_name = name_span.get_text(strip=True)
            sid_span = tds[2].find("span", class_="steam-id")
            if sid_span:
                steamid = sid_span.get_text(strip=True)

            # 内容
            msg_type = ""
            content = ""
            msg_td = tds[3]
            badge = msg_td.find("span", class_="aw-badge")
            if badge:
                msg_type = badge.get_text(strip=True)
                # Remove badge element to get remaining text
                badge.extract()
            content = msg_td.get_text(strip=True)

            return ChatMessage(
                time=time_text,
                server=server_text,
                map_name=map_text,
                player=player_name,
                steamid=steamid,
                msg_type=msg_type,
                content=content,
            )
        except Exception as e:
            logger.warning(f"[l4_chat] 解析消息行失败: {e}")
            return None

    async def get_chat_messages(
        self,
        server: str = "",
        page: int = 1,
    ) -> Union[List[ChatMessage], int]:
        """获取聊天记录

        Args:
            server: 服务器名，如 "Anne云服#1"，为空则全部
            page: 页码
        """
        params = []
        if server:
            from urllib.parse import quote

            params.append(f"server={quote(server)}")
        params.append(f"page={page}")
        url = f"{CHAT_URL}?{'&'.join(params)}"

        html = await self._fetch_html(url)
        if html is None:
            return -1

        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", class_="chat-table")
        if table is None:
            logger.warning("[l4_chat] 未找到聊天表格")
            return -1

        tbody = table.find("tbody") or table
        rows = tbody.find_all("tr")

        messages: List[ChatMessage] = []
        for tr in rows:
            msg = await self._parse_row(tr)
            if msg:
                messages.append(msg)

        logger.info(f"[l4_chat] 获取到 {len(messages)} 条聊天记录 (server={server}, page={page})")
        return messages


chat_api = ChatApi()
