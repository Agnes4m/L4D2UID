# L4D2UID

gsuid_core 插件，查询 L4D2 玩家数据（Anne 电信服）。

## 命令

| 触发 | 功能 |
|------|------|
| `l4查询` | 查询绑定/指定玩家统计（总榜 + 季度榜），返回图片 |
| `l4搜索` | 按名字搜索玩家 |
| `l4绑定` / `l4切换` / `l4删除` | 绑定/切换/删除 SteamID |
| `l4状态` | 服务器状态（全局统计 + 在线玩家列表），返回图片 |
| `l4统计` | 服务器荣誉殿堂（奖项/荣誉列表），返回图片 |
| `l4帮助` | 帮助图片 |

## 结构

| 路径 | 说明 |
|------|------|
| `l4_info/anne.py` | Anne 服玩家统计图片生成 |
| `l4_info/status.py` | 服务器状态 + 荣誉殿堂图片生成（含 `draw_awards_img`） |
| `l4_info/daidai.py` | 呆呆服 Playwright 截图 |
| `l4_info/panel_redesign.py` | 统计卡片 + 面板绘制 |
| `l4_info/pil_utils.py` | Colors 配色 + load_image |
| `l4_info/__init__.py` | 命令注册（查询/搜索/状态/统计） |
| `utils/api/request.py` | HTTP 客户端 + HTML 解析（含 `get_server_status` / `get_online_players` / `get_awards` / `get_statistics`） |
| `utils/api/api.py` | API URL 常量（含 `ANNEAWARDSAPI` / `ANNESTATISTICSAPI`） |
| `utils/api/models.py` | TypedDict 模型（含 `AnneStatus` / `AnneOnlinePlayer` / `AnneAward` / `AnneStatistics`） |
| `utils/l4_font.py` | 字体工具（基于 `gsuid_core.utils.fonts.fonts.core_font`，可能不支持 emoji） |
| `l4_user/__init__.py` | 绑定指令 |
| `l4_help/__init__.py` | 帮助指令 |

## API

| 名称 | 端点 |
|------|------|
| 状态 | `GET https://anne.trygek.com/stats/` |
| 统计 | `GET https://anne.trygek.com/stats/statistics/` |
| 荣誉 | `GET https://anne.trygek.com/stats/awards/` |
| 搜索 | `GET https://anne.trygek.com/stats/ranking/search.php?q=<keyword>` |
| 玩家 | `GET https://anne.trygek.com/stats/ranking/player.php?steamid=<id>` |
| 季度 | `GET https://anne.trygek.com/stats/ranking/player.php?steamid=<id>&quarter=YYYYQ` |

## 工具

- `uv` 管理依赖
- `ruff` 格式化/lint (line-length=120)
- Python >=3.12

## 配色

bg=#0a0e17, surface=#111827, accent=#38bdf8, text=#e2e8f0, muted=#94a3b8

## 暗色主题卡片尺寸

cards at 80+y, 210w, 50hgap, 25vgap

## 规范

- 双引号, 相对导入, pathlib, f-strings
- 无文档字符串, 最简注释
- ruff check 通过后提交
