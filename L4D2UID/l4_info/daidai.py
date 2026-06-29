from typing import Union

from gsuid_core.data_store import get_res_path
from playwright.async_api import async_playwright

from ..utils.api.api import DAIDAIPLAYERAPI

L4PATH = get_res_path("L4D2UID")


async def get_daidai_player_img(
    keyword: str,
) -> Union[str, bytes]:
    return await main(keyword)


async def main(name: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"{DAIDAIPLAYERAPI}{name}")

        await page.set_viewport_size({"width": 900, "height": 1200})


        new_path = L4PATH.joinpath("daidai_screenshot.png")
        await page.screenshot(path=new_path)  # 保存为图片
        await browser.close()  # 关闭浏览器
    with open(new_path, "rb") as f:
        img = f.read()
    return img
