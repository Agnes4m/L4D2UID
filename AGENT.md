# L4D2UID Agent Guide

## Project

L4D2UID - gsuid_core plugin for Left 4 Dead 2 player stats queries.

## Tools & Commands

- **Package manager**: `uv` (not pip/poetry)
- **Formatter**: `ruff format .`
- **Linter**: `ruff check .`
- **Python**: >=3.12

## Code Style

- Line length: 120
- Double quotes
- Modern type hints (`list[int]` not `List[int]`)
- Prefer pathlib, f-strings

## Key Structure

| Path | Purpose |
|------|---------|
| `L4D2UID/__init__.py` | Plugin entry (prefix `l4`) |
| `L4D2UID/l4_info/anne.py` | Anne server image generation |
| `L4D2UID/l4_info/daidai.py` | Daidai server screenshot |
| `L4D2UID/l4_info/panel_redesign.py` | Stats panel drawing |
| `L4D2UID/l4_info/pil_utils.py` | PIL helpers, Colors class |
| `L4D2UID/utils/api/request.py` | HTTP client + HTML parser |
| `L4D2UID/utils/api/api.py` | API URL constants |
| `L4D2UID/utils/api/models.py` | Typed dict models |
| `L4D2UID/l4_user/__init__.py` | User bind commands |
| `L4D2UID/l4_help/__init__.py` | Help command |

## Anne API

- Base: `https://anne.trygek.com/l4d_stats/ranking/`
- Search: GET with `?q=<keyword>`, returns HTML table
- Player: GET `player.php?steamid=<id>`, returns HTML

## Colors (dark theme)

- bg: `#0a0e17`, surface: `#111827`
- accent cyan: `#38bdf8`, accent teal: `#2dd4bf`
- text: `#e2e8f0`, text muted: `#94a3b8`

## Conventions

- Always run `ruff check .` before committing
- Use relative imports within the package
- CSS-like class names for Anne data extraction
- Use Playwright only for daidai server
