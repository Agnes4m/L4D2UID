"""L4D2 第三方地图搜索 - gamemaps.com"""

from gsuid_core.bot import Bot
from gsuid_core.data_store import get_res_path
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.sv import SV

from .api import game_maps_api
from .draw import draw_map_detail, draw_maps_list

l4_maps = SV("L4D2地图")


@l4_maps.on_command(("地图"), block=True)
async def send_l4_maps_msg(bot: Bot, ev: Event):
    """搜索/浏览 L4D2 第三方地图

    用法:
        l4地图              - 浏览地图 (从 /l4d2/maps)
        l4地图 数字ID       - 查看指定地图详情(如 l4地图 25582)
        l4地图 热门         - 热门地图
        l4地图 mod/模组     - 浏览模组 (从 /l4d2/mods)
        l4地图 co-op       - 按分类浏览
        l4地图 关键字       - 搜索地图
    """
    arg = ev.text.strip().lower()
    logger.info(f"[l4_maps] 命令参数: {arg}")

    if not arg:
        # 默认显示地图列表
        logger.info("[l4_maps] 获取地图列表...")
        maps = await game_maps_api.get_maps()
        if isinstance(maps, int):
            return await bot.send(f"获取地图列表失败 (错误码: {maps})")
        img = await draw_maps_list(maps, "地图")
        return await bot.send(img)

    # 纯数字 → 直接查地图详情
    if arg.isdigit():
        logger.info(f"[l4_maps] 查询地图详情: {arg}")
        detail = await game_maps_api.get_map_detail(arg)
        if isinstance(detail, int):
            return await bot.send(f"获取地图详情失败 (错误码: {detail})")
        img = await draw_map_detail(detail)
        return await bot.send(img)

    # 热门
    if arg in ("热门", "trending", "hot", "popular"):
        logger.info("[l4_maps] 获取热门地图...")
        maps = await game_maps_api.get_maps(sort="popular")
        if isinstance(maps, int):
            return await bot.send(f"获取热门地图失败 (错误码: {maps})")
        img = await draw_maps_list(maps, "热门地图")
        return await bot.send(img)

    # 模组
    if arg in ("mod", "模组"):
        logger.info("[l4_maps] 获取模组列表...")
        mods = await game_maps_api.get_mods()
        if isinstance(mods, int):
            return await bot.send(f"获取模组列表失败 (错误码: {mods})")
        img = await draw_maps_list(mods, "模组")
        return await bot.send(img)

    # 分类浏览
    categories = {
        "co-op": "co-op",
        "合作": "co-op",
        "versus": "versus",
        "对抗": "versus",
        "survival": "survival",
        "生存": "survival",
        "campaign": "campaign",
        "战役": "campaign",
        "mutation": "mutation",
        "突变": "mutation",
        "scavenge": "scavenge",
        "清道夫": "scavenge",
    }

    if arg in categories:
        cat = categories[arg]
        logger.info(f'[l4_maps] 获取分类 "{cat}" 的地图...')
        maps = await game_maps_api.get_maps_by_category(cat)
        if isinstance(maps, int):
            return await bot.send(f"获取分类地图失败 (错误码: {maps})")
        img = await draw_maps_list(maps, f"分类: {arg}")
        return await bot.send(img)

    # 搜索
    logger.info(f"[l4_maps] 搜索地图: {arg}")
    maps = await game_maps_api.search_maps(arg)
    if isinstance(maps, int):
        return await bot.send(f"搜索地图失败 (错误码: {maps})")
    if not maps:
        return await bot.send(f"没有找到与「{arg}」相关的地图")
    img = await draw_maps_list(maps, f"搜索: {arg}")
    await bot.send(img)


@l4_maps.on_command(("地图详情"), block=True)
async def send_l4_map_detail_msg(bot: Bot, ev: Event):
    """查看地图详情

    用法:
        l4地图详情 <id>     - 查看地图详情
    """
    map_id = ev.text.strip()
    if not map_id:
        return await bot.send("请提供地图 ID，例如: l4地图详情 35965")

    if not map_id.isdigit():
        return await bot.send("地图 ID 必须是数字")

    logger.info(f"[l4_maps] 获取地图详情: {map_id}")
    detail = await game_maps_api.get_map_detail(map_id)
    if isinstance(detail, int):
        return await bot.send(f"获取地图详情失败 (错误码: {detail})")
    img = await draw_map_detail(detail)
    await bot.send(img)


@l4_maps.on_command(("地图下载"), block=True)
async def send_l4_download_map_msg(bot: Bot, ev: Event):
    """下载地图文件

    用法:
        l4地图下载 <id>     - 下载地图文件到本地
    """
    map_id = ev.text.strip()
    if not map_id:
        return await bot.send("请提供地图 ID，例如: l4地图下载 25582")

    if not map_id.isdigit():
        return await bot.send("地图 ID 必须是数字")

    logger.info(f"[l4_maps] 下载地图: {map_id}")
    await bot.send(f"[l4] 正在获取地图 {map_id} 的下载链接...")

    dl_url = await game_maps_api.get_download_url(map_id)
    if isinstance(dl_url, int):
        return await bot.send(f"获取下载链接失败 (错误码: {dl_url})")

    # 先获取地图信息用于文件名
    detail = await game_maps_api.get_map_detail(map_id)
    file_name = f"l4d2_map_{map_id}"
    if not isinstance(detail, int):
        file_name = detail.get("file_name", f"l4d2_map_{map_id}")
        if file_name:
            # 保留扩展名
            import re

            m = re.search(r"\.(zip|vpk|rar|7z)", file_name, re.I)
            if m:
                file_name = f"l4d2_map_{map_id}{m.group(0)}"
            else:
                file_name = f"l4d2_map_{map_id}.zip"

    save_dir = get_res_path("L4D2UID") / "downloads"
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / file_name

    await bot.send(f"[l4] 开始下载 ({file_name})，文件较大请耐心等待...")

    # 使用 cloudscraper 下载文件
    try:
        import asyncio

        import cloudscraper

        scraper = cloudscraper.create_scraper()

        def _download():
            r = scraper.get(dl_url, stream=True, timeout=300)
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            return downloaded, total

        downloaded, total = await asyncio.get_event_loop().run_in_executor(None, _download)

        size_mb = downloaded / 1024 / 1024
        await bot.send(f"[l4] 下载完成！\n文件: {file_name}\n大小: {size_mb:.1f} MB")
        try:
            await bot.send(MessageSegment.file(save_path, file_name))
        except Exception as e:
            await bot.send(f"[l4] 上传到聊天失败: {e}\n文件已保存到本地: {save_path}")
        logger.info(f"[l4_maps] 下载完成: {save_path} ({size_mb:.1f} MB)")
    except Exception as e:
        logger.error(f"[l4_maps] 下载失败: {e}")
        # 文件下载失败时至少提供链接
        await bot.send(f"[l4] 文件较大，下载到本地失败: {e}\n直链(有时效性): {dl_url}\n建议用浏览器打开后下载。")
