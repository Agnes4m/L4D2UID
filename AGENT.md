# L4D2UID

gsuid_core 插件，查询 L4D2 玩家数据（Anne 电信服）。

## 命令

| 触发 | 功能 |
|------|------|
| `l4查询` | 查询绑定/指定玩家统计（总榜 + 季度榜），返回图片 |
| `l4搜索` | 按名字搜索玩家 |
| `l4绑定` / `l4切换` / `l4删除` | 绑定/切换/删除 SteamID |
| `l4状态` | 服务器状态（全局统计 + 在线玩家列表），返回图片 |
| `l4帮助` | 帮助图片 |

## 结构

| 路径 | 说明 |
|------|------|
| `l4_info/anne.py` | Anne 服玩家统计图片生成 |
| `l4_info/status.py` | 服务器状态图片生成 |
| `l4_info/daidai.py` | 呆呆服 Playwright 截图 |
| `l4_info/panel_redesign.py` | 统计卡片 + 面板绘制 |
| `l4_info/pil_utils.py` | Colors 配色 + load_image |
| `utils/api/request.py` | HTTP 客户端 + HTML 解析（含 `get_server_status` / `get_online_players`） |
| `utils/api/api.py` | API URL 常量 |
| `utils/api/models.py` | TypedDict 模型（含 `AnneStatus` / `AnneOnlinePlayer`） |
| `l4_user/__init__.py` | 绑定指令 |
| `l4_help/__init__.py` | 帮助指令 |

## API

- 状态: `GET https://anne.trygek.com/stats/`
- 搜索: `GET https://anne.trygek.com/stats/ranking/search.php?q=<keyword>`
- 玩家: `GET https://anne.trygek.com/stats/ranking/player.php?steamid=<id>`
- 季度: `GET https://anne.trygek.com/stats/ranking/player.php?steamid=<id>&quarter=YYYYQ`

## 工具

- `uv` 管理依赖
- `ruff` 格式化/lint (line-length=120)
- Python >=3.12

## 配色

bg=#0a0e17, surface=#111827, accent=#38bdf8, text=#e2e8f0, muted=#94a3b8

## 规范

- 双引号, 相对导入, pathlib, f-strings
- 无文档字符串, 最简注释
- ruff check 通过后提交
