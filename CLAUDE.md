# Excalidraw MCP Server

> Maaker.AI 开源 MCP Server，用自然语言生成 Excalidraw 图表

## 快速命令

```bash
# 开发
uv sync --dev
uv run pytest                    # 运行测试
uv run excalidraw-mcp            # 本地启动 MCP server

# 构建 & 发布（手动）
uv build                         # 构建到 dist/
uv publish --token <PYPI_TOKEN>  # 发布到 PyPI
```

## 自动发布到 PyPI

- **触发方式**：在 GitHub 创建 Release（打 tag）
- **工作流**：`.github/workflows/publish.yml`
- **认证方式**：PyPI Trusted Publisher（无需 token）
- **PyPI 项目**：https://pypi.org/project/maaker-excalidraw-mcp/

### 发版流程

1. 更新 `pyproject.toml` 中的 `version`
2. 提交并推送到 main
3. 在 GitHub 创建 Release，tag 格式 `v0.2.0`
4. GitHub Actions 自动构建并发布到 PyPI

### Trusted Publisher 配置（已完成）

PyPI 端配置：Owner=`maaker-ai`, Repo=`excalidraw-mcp`, Workflow=`publish.yml`, Environment=`pypi`

## 包信息

| 项目 | 值 |
|------|-----|
| PyPI 包名 | `maaker-excalidraw-mcp` |
| 入口命令 | `excalidraw-mcp` |
| GitHub | `maaker-ai/excalidraw-mcp` |
| 安装方式 | `claude mcp add excalidraw -- uvx maaker-excalidraw-mcp` |

## 目录结构

```
src/excalidraw_mcp/
├── server.py              # MCP server 入口，注册 5 个 tools
├── elements/              # Excalidraw 元素生成
│   ├── text.py            # 文本 + 带标签的形状（CJK 宽度估算）
│   ├── arrows.py          # 箭头（fixedPoint + orbit 绑定）
│   ├── shapes.py          # 矩形、椭圆、菱形
│   └── style.py           # 8 色预设
├── layout/                # 布局引擎
│   ├── sugiyama.py        # Sugiyama 分层布局（grandalf）— 流程图主引擎
│   └── grid.py            # 网格/分层布局 — 架构图使用
├── tools/                 # MCP 工具定义
│   ├── flowchart.py       # create_flowchart
│   ├── architecture.py    # create_architecture_diagram
│   ├── modify.py          # modify_diagram
│   ├── read.py            # read_diagram
│   └── export.py          # export_diagram
└── utils/
    ├── file_io.py         # save/load .excalidraw 文件
    ├── ids.py             # gen_id() 共享 ID 生成器
    └── svg_export.py      # SVG 导出
```

## 关键技术点

- **Sugiyama 布局**：使用 grandalf 库，处理分支/合并/循环/断连子图，支持 LR/RL/TB/BT 四方向
- **CJK 宽度**：中文 ~22px/字，英文 ~11px/字（fontSize=20）
- **箭头绑定**：使用 `fixedPoint` + `orbit` 模式（非已废弃的 focus/gap）
- **vertex 索引**：sugiyama.py 中用 index（非 label）作为 vertex data，避免重名冲突

## 技术栈

| 依赖 | 用途 |
|------|------|
| `mcp[cli]>=1.0.0` | MCP Python SDK |
| `grandalf>=0.8` | Sugiyama 分层图布局 |
| `hatchling` | 构建后端 |
| `pytest` | 测试 |
