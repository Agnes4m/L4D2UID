"""gamemaps.com API 客户端 - 使用 cloudscraper 绕过 Cloudflare 防护"""

from asyncio import sleep
from typing import List, Optional, Union

from bs4 import BeautifulSoup
from gsuid_core.logger import logger

from .models import GameMap, MapDetail

try:
    import cloudscraper

    _scraper = cloudscraper.create_scraper()
except ImportError:
    _scraper = None
    logger.warning("[l4_maps] cloudscraper 未安装，将使用 httpx（可能无法绕过 Cloudflare）")

    _scraper = None

GAMEMAPS_HOST = "https://www.gamemaps.com"
L4D2_URL = f"{GAMEMAPS_HOST}/l4d2"


class GameMapsApi:
    """gamemaps.com API 封装"""

    def __init__(self):
        self._session = None

    def _get_sync_scraper(self):
        """获取同步 scraper 实例"""
        if _scraper is not None:
            return _scraper
        return None

    async def _fetch_html(self, url: str) -> Optional[str]:
        """获取页面 HTML（同步 cloudscraper 封装为异步）"""
        scraper = self._get_sync_scraper()
        if scraper is None:
            logger.error("[l4_maps] cloudscraper 不可用，无法获取页面")
            return None

        for attempt in range(3):
            try:
                resp = await sleep(0, result=None)  # yield control
                # 使用 run_in_executor 避免阻塞事件循环
                import asyncio
                import functools

                func = functools.partial(scraper.get, url, timeout=30)
                resp = await asyncio.get_event_loop().run_in_executor(None, func)
                if resp.status_code == 200:
                    return resp.text
                elif resp.status_code == 403:
                    logger.warning(f"[l4_maps] 请求被拒绝(403): {url}")
                    return None
                else:
                    logger.warning(
                        f"[l4_maps] 请求失败 (第{attempt + 1}/3次): "
                        f"status={resp.status_code}"
                    )
                    if attempt < 2:
                        await sleep(2)
            except Exception as e:
                logger.warning(
                    f"[l4_maps] 请求异常 (第{attempt + 1}/3次): {e}"
                )
                if attempt < 2:
                    await sleep(2)
        return None

    async def _parse_map_item(self, article) -> Optional[GameMap]:
        """解析单个地图列表项 article 元素"""
        try:
            item_id = article.get("data-id", "")
            if not item_id:
                return None

            # 标题
            title_el = article.find(class_="title")
            title = title_el.get("title", "") if title_el else ""

            # 缩略图
            thumb = ""
            img = article.find("img", class_="thumbnail")
            if not img:
                img = article.find("img", alt=title)
            if img:
                thumb = img.get("src", "")
                # 补全为完整 URL（HTML 中是相对路径）
                if thumb.startswith("/"):
                    thumb = f"{GAMEMAPS_HOST}{thumb}"
                logger.debug(f"[l4_maps] 缩略图URL: {thumb}")

            # 作者
            author = ""
            author_url = ""
            byline = article.find(class_="byline")
            if byline:
                author_link = byline.find("a")
                if author_link:
                    author_span = author_link.find(class_="title")
                    if author_span:
                        author = author_span.get_text(strip=True)
                    author_url = author_link.get("href", "")

            # 评分
            rating_el = article.find(class_="rating")
            rating = rating_el.get_text(strip=True) if rating_el else "N/A"
            rating_title = rating_el.get("title", "") if rating_el else ""

            # 描述
            desc_p = article.find("p")
            desc = desc_p.get_text(strip=True) if desc_p else ""

            # 日期
            date_el = article.find("time")
            date = date_el.get("datetime", "") if date_el else ""
            if not date and date_el:
                date = date_el.get_text(strip=True)

            # 查看数
            views = ""
            views_el = article.find(class_="views")
            if views_el:
                val_el = views_el.find(class_="value")
                if val_el:
                    views = val_el.get_text(strip=True)

            # 类型标签 (如 "5 Maps", "Mod")
            type_label = ""
            type_el = article.find(class_="type")
            if type_el:
                type_label = type_el.get_text(strip=True)

            # 状态 (Updated, New 等)
            states: List[str] = []
            states_ul = article.find("ul", class_="states")
            if states_ul:
                for li in states_ul.find_all("li"):
                    states.append(li.get_text(strip=True))

            url = f"{GAMEMAPS_HOST}/details/{item_id}"

            return GameMap(
                id=item_id,
                title=title,
                thumb=thumb,
                author=author,
                author_url=author_url,
                rating=rating,
                rating_title=rating_title,
                views=views,
                date=date,
                description=desc,
                type_label=type_label,
                states=states,
                url=url,
            )
        except Exception as e:
            logger.warning(f"[l4_maps] 解析地图项失败: {e}")
            return None

    async def get_latest_maps(self) -> Union[List[GameMap], int]:
        """获取最新发布的地图"""
        html = await self._fetch_html(L4D2_URL)
        if html is None:
            return -1

        soup = BeautifulSoup(html, "lxml")

        # 查找 Latest Releases 节
        items: List[GameMap] = []
        seen_ids: set = set()

        for slider in soup.find_all(class_="item-slide-list"):
            parent = slider.find_parent()
            if parent:
                h = parent.find(["h1", "h2", "h3"])
                header_text = h.get_text(strip=True) if h else ""
                if "Latest Releases" in header_text:
                    for article in slider.find_all(class_="list-item-file"):
                        parsed = await self._parse_map_item(article)
                        if parsed and parsed["id"] not in seen_ids:
                            seen_ids.add(parsed["id"])
                            items.append(parsed)
                    break

        # 如果没找到 Latest Releases，回退到第一个非 Featured 的 slider
        if not items:
            for slider in soup.find_all(class_="item-slide-list"):
                parent = slider.find_parent()
                if parent:
                    h = parent.find(["h1", "h2", "h3"])
                    header_text = h.get_text(strip=True) if h else ""
                    if "Featured" not in header_text:
                        for article in slider.find_all(class_="list-item-file"):
                            parsed = await self._parse_map_item(article)
                            if parsed and parsed["id"] not in seen_ids:
                                seen_ids.add(parsed["id"])
                                items.append(parsed)
                        if items:
                            break

        logger.info(f"[l4_maps] 获取到 {len(items)} 个最新地图")
        return items[:20]

    async def get_trending_maps(self) -> Union[List[GameMap], int]:
        """获取热门地图"""
        html = await self._fetch_html(L4D2_URL)
        if html is None:
            return -1

        soup = BeautifulSoup(html, "lxml")
        items: List[GameMap] = []
        seen_ids: set = set()

        for slider in soup.find_all(class_="item-slide-list"):
            parent = slider.find_parent()
            if parent:
                h = parent.find(["h1", "h2", "h3"])
                header_text = h.get_text(strip=True) if h else ""
                if "Trending Maps" in header_text:
                    for article in slider.find_all(class_="list-item-file"):
                        parsed = await self._parse_map_item(article)
                        if parsed and parsed["id"] not in seen_ids:
                            seen_ids.add(parsed["id"])
                            items.append(parsed)
                    break

        logger.info(f"[l4_maps] 获取到 {len(items)} 个热门地图")
        return items[:15]

    async def get_maps_by_category(
        self, category: str, page: int = 1
    ) -> Union[List[GameMap], int]:
        """按分类获取地图

        Args:
            category: 分类名 (co-op, versus, survival, campaign, mutation, scavenge, etc.)
            page: 页码 (默认 1)
        """
        url = f"{L4D2_URL}/{category}/"
        if page > 1:
            url += f"?page={page}"

        html = await self._fetch_html(url)
        if html is None:
            return -1

        soup = BeautifulSoup(html, "lxml")
        items: List[GameMap] = []
        seen_ids: set = set()

        for article in soup.find_all(class_="list-item-file"):
            parsed = await self._parse_map_item(article)
            if parsed and parsed["id"] not in seen_ids:
                seen_ids.add(parsed["id"])
                items.append(parsed)

        logger.info(
            f"[l4_maps] 分类 \"{category}\" 第{page}页: 获取到 {len(items)} 个地图"
        )
        return items

    async def get_maps(
        self, sort: str = "recent", page: int = 1
    ) -> Union[List[GameMap], int]:
        """获取地图列表（从 /l4d2/maps）

        Args:
            sort: 排序方式 (recent, popular, rviews)
            page: 页码 (默认 1)
        """
        url = f"{L4D2_URL}/maps"
        params = []
        if sort and sort != "recent":
            params.append(f"sort={sort}")
        if page > 1:
            params.append(f"page={page}")
        if params:
            url += "?" + "&".join(params)

        html = await self._fetch_html(url)
        if html is None:
            return -1

        soup = BeautifulSoup(html, "lxml")
        items: List[GameMap] = []
        seen_ids: set = set()

        for article in soup.find_all(class_="list-item-file"):
            parsed = await self._parse_map_item(article)
            if parsed and parsed["id"] not in seen_ids:
                seen_ids.add(parsed["id"])
                items.append(parsed)

        logger.info(f"[l4_maps] 地图列表 (sort={sort}, page={page}): {len(items)} 个")
        return items

    async def get_mods(
        self, sort: str = "recent", page: int = 1
    ) -> Union[List[GameMap], int]:
        """获取模组列表（从 /l4d2/mods）"""
        url = f"{L4D2_URL}/mods"
        params = []
        if sort and sort != "recent":
            params.append(f"sort={sort}")
        if page > 1:
            params.append(f"page={page}")
        if params:
            url += "?" + "&".join(params)

        html = await self._fetch_html(url)
        if html is None:
            return -1

        soup = BeautifulSoup(html, "lxml")
        items: List[GameMap] = []
        seen_ids: set = set()

        for article in soup.find_all(class_="list-item-file"):
            parsed = await self._parse_map_item(article)
            if parsed and parsed["id"] not in seen_ids:
                seen_ids.add(parsed["id"])
                items.append(parsed)

        logger.info(f"[l4_maps] 模组列表 (sort={sort}, page={page}): {len(items)} 个")
        return items

    async def search_maps(self, keyword: str) -> Union[List[GameMap], int]:
        """搜索地图

        由于 /search/l4d2 端点有额外的 Cloudflare 防护无法直接调用，
        采用并发抓取 /l4d2/maps 多页内容进行客户端侧匹配。
        """
        if not keyword or not keyword.strip():
            return await self.get_maps()

        keyword_lower = keyword.strip().lower()
        results: List[GameMap] = []
        seen_ids: set = set()

        import asyncio

        # 并发获取前 3 页
        async def _fetch_page(p: int) -> list:
            url = f"{L4D2_URL}/maps?page={p}"
            html = await self._fetch_html(url)
            if html is None:
                return []
            soup = BeautifulSoup(html, "lxml")
            items = []
            for article in soup.find_all(class_="list-item-file"):
                parsed = await self._parse_map_item(article)
                if parsed and parsed["id"] not in seen_ids:
                    seen_ids.add(parsed["id"])
                    if (
                        keyword_lower in parsed["title"].lower()
                        or keyword_lower in parsed["description"].lower()
                        or keyword_lower in parsed["author"].lower()
                    ):
                        items.append(parsed)
            return items

        pages_results = await asyncio.gather(
            _fetch_page(1), _fetch_page(2), _fetch_page(3),
            return_exceptions=True,
        )

        for pr in pages_results:
            if isinstance(pr, list):
                results.extend(pr)
            if len(results) >= 20:
                break

        logger.info(f"[l4_maps] 搜索 \"{keyword}\": 找到 {len(results)} 个结果")
        return results[:20]

    async def get_map_detail(self, map_id: str) -> Union[MapDetail, int]:
        """获取地图详情"""
        url = f"{GAMEMAPS_HOST}/details/{map_id}"
        html = await self._fetch_html(url)
        if html is None:
            return -1

        soup = BeautifulSoup(html, "lxml")

        try:
            # 标题
            title_el = soup.find("h1")
            title = title_el.get_text(strip=True) if title_el else ""

            # 类型标签 - 从页面标签中提取
            type_label = ""
            # 尝试从详情页的标签中推断类型
            tags_section = soup.find(class_="tags")
            if tags_section:
                for li in tags_section.find_all("li"):
                    tag_el = li.find(class_="bubble-button") or li.find("a")
                    if tag_el:
                        t = tag_el.get_text(strip=True)
                        if "Map" in t and any(c.isdigit() for c in t):
                            type_label = t
                            break
                        elif "Map" in t:
                            type_label = t
                        elif t == "Mod":
                            type_label = t

            # 主图 (media-holder)
            main_image = ""
            media_holder = soup.find(class_="media-holder")
            if media_holder:
                img = media_holder.find("img")
                if img:
                    src = img.get("src", "")
                    main_image = f"{GAMEMAPS_HOST}{src}" if src.startswith("/") else src

            # 所有截图（从 /ss/ 路径）
            screenshots: List[str] = []
            seen: set = set()
            for img in soup.find_all("img"):
                src = img.get("src", "")
                if "/ss/" in src and src not in seen:
                    seen.add(src)
                    full = f"{GAMEMAPS_HOST}{src}" if src.startswith("/") else src
                    screenshots.append(full)

            # 描述
            description = ""
            desc_section = soup.find(class_="desc")
            if desc_section:
                pre = desc_section.find("pre")
                if pre:
                    description = pre.get_text(strip=True)

            # 作者
            author = ""
            author_url = ""
            dev_section = soup.find(class_="developers")
            if dev_section:
                user_preview = dev_section.find(class_="user-preview")
                if user_preview:
                    username_el = user_preview.find(class_="username")
                    if username_el:
                        a = username_el.find("a")
                        if a:
                            author = a.get_text(strip=True)
                            author_url = a.get("href", "")
                        else:
                            author = username_el.get_text(strip=True)

            # 文件信息
            file_name = ""
            file_size = ""
            file_date = ""
            version = ""
            info_cards = soup.find_all(class_="info-card")
            for card in info_cards:
                card_text = card.get_text(strip=True)
                if ".zip" in card_text or ".vpk" in card_text:
                    p_tags = card.find_all("p")
                    if len(p_tags) >= 1:
                        file_name = p_tags[0].get("title", "") or p_tags[0].get_text(strip=True)
                    if len(p_tags) >= 2:
                        date_size = p_tags[1].get_text(strip=True)
                        import re

                        m = re.match(r"(.+?)\s*\((.+)\)", date_size)
                        if m:
                            file_date = m.group(1).strip()
                            file_size = m.group(2).strip()
                        else:
                            file_date = date_size
                elif "Changelog" in card_text:
                    p_tags = card.find_all("p")
                    if len(p_tags) >= 2:
                        version = p_tags[1].get_text(strip=True)

            # 标签
            tags: List[str] = []
            if tags_section:
                for li in tags_section.find_all("li"):
                    tag_el = li.find(class_="bubble-button") or li.find("a")
                    if tag_el:
                        tags.append(tag_el.get_text(strip=True))

            # 特性
            features: List[str] = []
            features_section = soup.find(class_="features")
            if features_section:
                for li in features_section.find_all("li"):
                    features.append(li.get_text(strip=True))

            # 评分
            rating = "N/A"
            rating_el = soup.find(class_="rating")
            if rating_el:
                rating = rating_el.get_text(strip=True)

            # 浏览数 (views)
            views = ""
            views_el = soup.find(class_="views")
            if views_el:
                views = views_el.get_text(strip=True)

            # 评价数
            reviews_count = ""
            import re
            m = re.search(r"Reviews\s*\((\d+)\)", html)
            if m:
                reviews_count = m.group(1)

            # 获奖数
            awards_count = ""
            m2 = re.search(r"(\d+)\s*Awards?", html)
            if m2:
                awards_count = m2.group(1)

            # 平台
            platform = ""
            plat_el = soup.find("li", class_="plat")
            if plat_el:
                platform = plat_el.get_text(strip=True)

            return MapDetail(
                id=map_id,
                title=title,
                type_label=type_label,
                main_image=main_image,
                screenshots=screenshots,
                description=description,
                author=author,
                author_url=author_url,
                file_name=file_name,
                file_size=file_size,
                file_date=file_date,
                version=version,
                tags=tags,
                features=features,
                rating=rating,
                views=views,
                reviews_count=reviews_count,
                awards_count=awards_count,
                platform=platform,
                download_url=f"{GAMEMAPS_HOST}/downloads/download",
            )
        except Exception as e:
            logger.error(f"[l4_maps] 解析地图详情失败: {e}")
            return -1

    async def get_download_url(self, map_id: str) -> Union[str, int]:
        """获取地图文件的下载直链

        Returns:
            成功时返回下载 URL（有时效性）
            失败时返回错误码
        """
        url = f"{GAMEMAPS_HOST}/downloads/download"
        logger.info(f"[l4_maps] 获取下载链接: {map_id}")

        # 先用 cloudscraper 访问详情页建立 session
        scraper = self._get_sync_scraper()
        if scraper is None:
            return -1

        import asyncio
        import functools

        try:
            # 先访问详情页
            func = functools.partial(
                scraper.get,
                f"{GAMEMAPS_HOST}/details/{map_id}",
                timeout=15,
            )
            await asyncio.get_event_loop().run_in_executor(None, func)

            # POST 获取下载重定向
            func = functools.partial(
                scraper.post,
                url,
                data={"ids[]": map_id, "noqueue": "true", "direct": "true"},
                allow_redirects=False,
                headers={"Referer": f"{GAMEMAPS_HOST}/details/{map_id}"},
                timeout=15,
            )
            resp = await asyncio.get_event_loop().run_in_executor(None, func)

            if resp.status_code == 302:
                from urllib.parse import urljoin

                dl_path = resp.headers.get("Location", "")
                if dl_path:
                    dl_url = urljoin(GAMEMAPS_HOST, dl_path)
                    logger.info(f"[l4_maps] 下载链接: {dl_url}")
                    return dl_url

            logger.warning(f"[l4_maps] 获取下载链接失败: status={resp.status_code}")
            return -1
        except Exception as e:
            logger.error(f"[l4_maps] 获取下载链接异常: {e}")
            return -1


game_maps_api = GameMapsApi()
