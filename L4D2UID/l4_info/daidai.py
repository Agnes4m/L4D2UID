"""
L4D2 呆呆服信息查询模块

功能：
- 使用 Playwright 渲染呆呆服web页面获取玩家信息
- 将页面截图作为图片返回
"""

from typing import Union

from playwright.async_api import async_playwright

from gsuid_core.data_store import get_res_path
from gsuid_core.plugins.L4D2UID.L4D2UID.utils.api.api import DAIDAIPLAYERAPI

L4PATH = get_res_path("L4D2UID")


async def get_daidai_player_img(
    keyword: str,
) -> Union[str, bytes]:
    return await main(keyword)


async def main(name: str):
    # 使用 Playwright 渲染 HTML
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"{DAIDAIPLAYERAPI}{name}")

        # 设置视口
        await page.set_viewport_size({"width": 900, "height": 1200})

        # rendered_html = await page.content()
        # print(rendered_html)

        new_path = L4PATH.joinpath("CS2UID/name.png")
        await page.screenshot(path=new_path)  # 保存为图片
        await browser.close()  # 关闭浏览器
    with open(new_path, "rb") as f:
        img = f.read()
    return img
