from typing import TypedDict


class ChatMessage(TypedDict):
    """聊天消息"""

    time: str
    server: str
    map_name: str
    player: str
    steamid: str
    msg_type: str  # e.g. "团队", "公开", ""
    content: str
