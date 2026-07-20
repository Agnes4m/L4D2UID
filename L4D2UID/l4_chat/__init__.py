"""Anne 游戏聊天记录查询"""

from collections import defaultdict

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.l4_config import l4d2_config
from .api import chat_api
from .draw import draw_chat_messages

l4_chat = SV("L4D2聊天")

SERVERS_MAP = {str(i): f"Anne云服#{i}" for i in range(1, 74)}


@l4_chat.on_command(("聊天"), block=True)
async def send_l4_chat_msg(bot: Bot, ev: Event):
    """查看 Anne 服务器聊天记录

    用法:
        l4聊天              - 最近 N 条（配置 chat_default_count）
        l4聊天 30           - 最近 30 条
        l4聊天 云1          - Anne云服#1 最近 N 条
        l4聊天 云1 30       - Anne云服#1 最近 30 条
        l4聊天 云1 100      - Anne云服#1 最近 100 条（自动翻页）
        l4聊天 云1 30 2     - Anne云服#1 第2页 30条
    """
    raw = ev.text.strip()
    logger.info(f"[l4_chat] 命令参数: {raw}")

    # 从配置读取默认值
    server = l4d2_config.get_config("chat_default_server").data or ""
    count = int(l4d2_config.get_config("chat_default_count").data)
    page = 1

    if raw:
        parts = raw.split()
        # 解析服务器
        for p in parts:
            if p.startswith("云") and p[1:].isdigit():
                num = p[1:]
                if num in SERVERS_MAP:
                    server = SERVERS_MAP[num]
                break

        # 解析数量
        count_parts = [p for p in parts if p.isdigit()]
        if count_parts:
            count = int(count_parts[0])
            if count < 1:
                count = 1
            if count > 200:
                count = 200

        # 解析页码
        if len(count_parts) >= 2:
            page = int(count_parts[1])
            if page < 1:
                page = 1

    # 计算需要翻页数
    per_page = 50
    pages_needed = (count + per_page - 1) // per_page

    all_messages = []
    for p in range(page, page + pages_needed):
        msgs = await chat_api.get_chat_messages(server=server, page=p)
        if isinstance(msgs, int):
            if all_messages:
                break
            return await bot.send(f"获取聊天记录失败 (错误码: {msgs})")
        all_messages.extend(msgs)
        if len(all_messages) >= count:
            break

    all_messages = all_messages[:count]

    if not all_messages:
        return await bot.send("没有找到聊天记录")

    # 按服务器分组（仅取服务器名部分，去掉模式信息）
    groups = defaultdict(list)
    for msg in all_messages:
        full = msg.get("server", "") or ""
        # 截取到第一个 [ 之前的纯服务器名
        idx = full.find("[")
        srv = full[:idx].strip() if idx > 0 else full
        if not srv:
            srv = "未知服务器"
        groups[srv].append(msg)

    server_name = server if server else "全部服务器"
    img = await draw_chat_messages(
        groups,
        server_name=server_name,
    )
    await bot.send(img)
