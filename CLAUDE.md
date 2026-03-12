# Excalidraw MCP Server

> Maaker.AI 开源 MCP Server，用自然语言生成 Excalidraw 图表

## 快速命令

```bash
# 开发
uv sync --dev
uv run pytest                    # 运行测试（91+ tests）
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
3. 在 GitHub 创建 Release，tag 格式 `v0.x.0`
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
├── server.py              # MCP server 入口，注册 10 个 tools
├── elements/              # Excalidraw 元素生成
│   ├── text.py            # 文本 + 带标签的形状（CJK 宽度估算，多行支持）
│   ├── arrows.py          # 箭头（fixedPoint + orbit，边标签，肘形路由）
│   ├── shapes.py          # 矩形、椭圆、菱形
│   ├── groups.py          # 分组框架（虚线背景矩形 + 标签）
│   └── style.py           # 8 色基础 + 30+ 技术品牌色
├── layout/                # 布局引擎
│   ├── sugiyama.py        # Sugiyama 分层布局（grandalf）— 流程图主引擎
│   └── grid.py            # 网格/分层布局 — 架构图使用
├── tools/                 # MCP 工具定义
│   ├── flowchart.py       # create_flowchart（形状/分组/边标签/线型）
│   ├── architecture.py    # create_architecture_diagram（连接标签/组件色）
│   ├── sequence.py        # create_sequence_diagram（UML 时序图）
│   ├── mindmap.py         # create_mindmap（树形思维导图）
│   ├── er_diagram.py      # create_er_diagram（ER 实体关系图）
│   ├── mermaid.py         # import_mermaid_flowchart（Mermaid 导入）
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
- **边标签**：text 元素的 containerId 指向 arrow id，arrow 的 boundElements 包含 text 引用
- **多行标签**：`\n` 分割，宽度取最长行，高度自动扩展
- **技术品牌色**：redis/postgres/kafka/docker/k8s/react/python/aws 等 30+ 颜色

## 技术栈

| 依赖 | 用途 |
|------|------|
| `mcp[cli]>=1.0.0` | MCP Python SDK |
| `grandalf>=0.8` | Sugiyama 分层图布局 |
| `hatchling` | 构建后端 |
| `pytest` | 测试 |
