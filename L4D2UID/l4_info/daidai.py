from pathlib import Path
from typing import Union

from gsuid_core.data_store import get_res_path
from playwright.async_api import async_playwright
from gsuid_core.plugins.L4D2UID.L4D2UID.utils.api.api import DAIDAIPLAYERAPI

TEXTURED = Path(__file__).parent / "texture2d" / "anne"
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
        await page.goto(f'{DAIDAIPLAYERAPI}{name}')

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
