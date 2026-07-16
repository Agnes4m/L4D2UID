from typing import List, TypedDict


class GameMap(TypedDict):
    """地图列表项"""
    id: str
    title: str
    thumb: str
    author: str
    author_url: str
    rating: str
    rating_title: str
    views: str
    date: str
    description: str
    type_label: str  # e.g. "5 Maps", "Mod"
    states: List[str]  # e.g. ["Updated", "New"]
    url: str


class MapDetail(TypedDict):
    """地图详情"""
    id: str
    title: str
    type_label: str  # e.g. "5 Maps", "Mod"
    main_image: str
    screenshots: List[str]  # 多张截图 URL
    description: str
    author: str
    author_url: str
    file_name: str
    file_size: str
    file_date: str
    version: str
    tags: List[str]
    features: List[str]
    rating: str
    views: str  # e.g. "267.8K"
    reviews_count: str  # e.g. "11"
    awards_count: str  # e.g. "8"
    platform: str  # e.g. "Windows"
    download_url: str
