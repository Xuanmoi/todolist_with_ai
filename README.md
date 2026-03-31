# Obsidian Todo AI

智能 TodoList 管理系统，与 Obsidian 无缝集成，通过 DeepSeek AI 自动生成每日任务、分析完成情况、给出优化建议。

## 环境部署（首次安装）

如果是第一次使用，或换了新电脑，需要先完成以下步骤。

### 前置条件

- macOS 系统
- Python 3.9+（macOS 自带，终端输入 `python3 --version` 确认）
- [Obsidian](https://obsidian.md/) 已安装，Vault 路径为 `/Users/qbq/Documents/Obsidian Vault`

> 如果 Vault 路径不同，修改 `config.yaml` 中的 `vault_path` 即可。

### 安装步骤

```bash
# 1. 进入项目目录
cd /Users/qbq/learn/todolist

# 2. 创建 Python 虚拟环境
python3 -m venv .venv

# 3. 激活虚拟环境
source .venv/bin/activate

# 4. 安装依赖
pip install --upgrade pip
pip install -e .

# 5. 初始化 Obsidian 目录结构
todo init

# 6. （可选）注册每日定时任务，每天 9:05 自动运行
cp com.obsidian-todo-ai.daily.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.obsidian-todo-ai.daily.plist
```

安装完成后，可以运行 `todo --help` 验证是否成功。

## 快速开始

### 1. 配置 DeepSeek API Key

编辑项目根目录下的 `config.yaml`，填入你的 DeepSeek API Key：

```yaml
ai:
  api_key: "sk-your-api-key-here"
```

> 获取 API Key：https://platform.deepseek.com/
>
> 不配置也能使用，但每日任务会使用通用模板，无法根据你的目标和完成情况智能生成。

### 2. 启动项目

每次使用前，需要在终端中进入项目目录并激活虚拟环境：

```bash
cd /Users/qbq/learn/todolist
source .venv/bin/activate
```

激活成功后，终端提示符前会出现 `(.venv)` 标记，此时就可以使用 `todo` 命令了。

> **虚拟环境只影响当前终端窗口**，关闭窗口自动失效，不会影响系统其他部分。

### 3. 关闭项目

使用完毕后，在终端中输入：

```bash
deactivate
```

或者直接关闭终端窗口即可。

### 4. 初始化（仅首次使用）

首次使用时，运行以下命令创建 Obsidian 中的目录结构：

```bash
todo init
```

## 每日任务

### 任务从哪里来？

| 方式 | 谁来写 | 什么时候 |
|------|--------|----------|
| AI 自动生成 | DeepSeek | 每天 9:05 自动运行（需配置 API Key） |
| 命令行添加 | 你自己 | 随时通过 `todo add` 命令 |
| Obsidian 编辑 | 你自己 | 随时在 Obsidian 中打开当天 `.md` 文件手动添加 |

配置了 API Key 后，AI 会根据你的**阶段性目标**和**近 7 天完成情况**智能生成任务，自动调整数量和难度。

### 每日任务命令

```bash
# AI 回顾昨天完成情况 + 智能生成今天任务（推荐）
todo daily-run

# 不使用 AI，用通用模板生成（离线模式）
todo daily-run --no-ai

# 查看今日 Todo 列表
todo today

# 添加一个普通优先级任务
todo add "整理房间"

# 添加一个高优先级任务
todo add "准备面试" -p high
```

### 在 Obsidian 中完成任务

打开 `TodoList/Daily/` 下当天的文件，直接点击复选框勾选：

```
- [ ] 未完成  →  点一下  →  - [x] 已完成
```

## 目标管理

目标分为长期和短期，区别在于截止日期的远近，系统会根据所有目标综合生成每日任务。

### 创建目标

```bash
# 创建长期目标（截止日期较远），AI 自动拆解为里程碑
todo goal add "韩语学习" -d "从零基础到能进行日常对话" --deadline 2026-09-30

# 创建短期目标（截止日期较近）
todo goal add "五一旅行准备" -d "规划行程、订酒店、收拾行李" --deadline 2026-05-01

# 不使用 AI 拆解，自己在 Obsidian 里填写里程碑
todo goal add "读书计划" -d "每月读两本书" --no-ai-decompose

# 不指定截止日期（后续可在 Obsidian 中补充）
todo goal add "学做饭" -d "每周学一道新菜"
```

执行后，AI 会将目标拆解为 5-8 个里程碑，生成到 Obsidian 的 `TodoList/Goals/` 目录下。

### 查看所有目标

```bash
todo goal list
```

### 在 Obsidian 中修改目标

目标文件是普通 Markdown，存放在 `TodoList/Goals/` 目录下，直接在 Obsidian 中打开编辑：

- **改截止日期** → 修改 `截止日期：xxxx-xx-xx` 那一行
- **增删里程碑** → 编辑 `## 🏁 里程碑` 下面的 `- [ ]` 条目
- **改目标描述** → 修改 `## 📖 描述` 下面的文字
- **完成里程碑** → 把 `- [ ]` 改为 `- [x]`，或直接点击复选框

改完保存即可，系统下次运行时会读取最新内容。

## 统计与回顾

```bash
# 查看近 7 天完成统计
todo stats

# 查看近 14 天完成统计
todo stats -n 14

# 触发 AI 回顾分析（给出建议和改进方向）
todo review

# 生成每周回顾报告（保存到 Obsidian）
todo weekly
```

## 工作流程

```
设定阶段性目标 → AI 拆解为里程碑
        ↓
每天 9:05 自动运行 → AI 分析完成情况，智能生成当日任务
        ↓
在 Obsidian 中勾选完成 → 打开 TodoList/Daily/ 下当天的文件
        ↓
AI 分析并给建议 → 自动调整后续任务安排
```

## 在 Obsidian 中使用

1. 打开 Obsidian，仓库路径为 `/Users/qbq/Documents/Obsidian Vault`
2. 在左侧文件浏览器找到 `TodoList/` 文件夹
3. 每天查看 `TodoList/Daily/` 下当天日期的文件（如 `2026-03-31.md`）
4. 直接点击复选框勾选已完成的任务
5. 目标文件（`Goals/`）中的里程碑也可以同样勾选
6. 文件之间通过 `[[韩语学习]]` 等双向链接点击跳转

### 文件结构

```
Obsidian Vault/
└── TodoList/
    ├── Goals/          # 阶段性目标（韩语学习.md、视频剪辑.md ...）
    ├── Daily/          # 每日 Todo（2026-03-31.md、2026-04-01.md ...）
    ├── Reviews/        # 周报/月报
    └── AI-Suggestions/ # AI 每日建议记录
```

## 定时任务管理

系统通过 macOS launchd 管理定时任务，每天 9:05 自动运行 `todo daily-run`。

```bash
# 查看定时任务是否正常注册
launchctl list | grep obsidian-todo

# 手动触发一次（不用等到明天 9:05）
launchctl start com.obsidian-todo-ai.daily

# 停用定时任务
launchctl unload ~/Library/LaunchAgents/com.obsidian-todo-ai.daily.plist

# 重新启用定时任务
launchctl load ~/Library/LaunchAgents/com.obsidian-todo-ai.daily.plist
```

> 定时任务的运行日志在项目的 `logs/` 目录下，可以查看每次运行是否成功。

## 所有命令速查

| 命令 | 说明 |
|------|------|
| `todo init` | 初始化目录结构（仅首次） |
| `todo daily-run` | 每日运行：回顾昨天 + AI 生成今天任务 |
| `todo daily-run --no-ai` | 每日运行（不使用 AI） |
| `todo today` | 查看今日任务列表 |
| `todo add "任务" -p high` | 添加高优先级任务 |
| `todo add "任务"` | 添加普通优先级任务 |
| `todo goal add "名称" -d "描述"` | 创建新目标（AI 拆解里程碑） |
| `todo goal add "名称" -d "描述" --deadline 2026-12-31` | 创建带截止日期的目标 |
| `todo goal add "名称" -d "描述" --no-ai-decompose` | 创建目标（不用 AI 拆解） |
| `todo goal list` | 查看所有活跃目标 |
| `todo stats` | 查看近 7 天完成统计 |
| `todo stats -n 14` | 查看近 14 天完成统计 |
| `todo review` | 触发 AI 回顾分析 |
| `todo weekly` | 生成每周回顾报告 |

## 当前目标

| 目标 | 截止日期 | 描述 |
|------|----------|------|
| 韩语学习 | 2026-09-30 | 从零基础到日常对话，能看懂简单韩剧字幕 |
| 视频剪辑 | 2026-09-30 | 学会视频剪辑，能独立完成 Vlog 和短视频制作 |
