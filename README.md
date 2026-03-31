# Obsidian Todo AI

智能 TodoList 管理系统，与 Obsidian 无缝集成，通过 DeepSeek AI 自动生成每日任务、分析完成情况、给出优化建议。

## 快速开始

### 1. 配置 DeepSeek API Key

编辑 `config.yaml`，填入你的 DeepSeek API Key：

```yaml
ai:
  api_key: "sk-your-api-key-here"
```

> 获取 API Key：https://platform.deepseek.com/

### 2. 激活虚拟环境

```bash
source .venv/bin/activate
```

### 3. 常用命令

```bash
# 每日自动运行（AI 回顾昨天 + 生成今天任务）
todo daily-run

# 不使用 AI（离线模式）
todo daily-run --no-ai

# 查看今日 Todo
todo today

# 添加临时任务
todo add "修复Bug" -p high

# 查看目标列表
todo goal list

# 添加新目标（AI 会自动拆解为里程碑）
todo goal add "新目标名称" -d "目标描述"

# 查看近 7 天统计
todo stats

# 触发 AI 回顾分析
todo review

# 生成每周报告
todo weekly
```

## 目标管理

### 创建新目标

```bash
# AI 自动拆解里程碑
todo goal add "健身计划" -d "每周锻炼3次，体重减到70kg" --deadline 2026-08-01

# 不使用 AI，手动管理里程碑
todo goal add "读书计划" -d "每月读两本书" --no-ai-decompose
```

### 在 Obsidian 中修改目标

目标文件是普通 Markdown，存放在 `TodoList/Goals/` 目录下，可以直接在 Obsidian 中打开编辑：

- **改截止日期** → 修改 `截止日期：xxxx-xx-xx` 那一行
- **增删里程碑** → 直接编辑 `## 🏁 里程碑` 下面的 `- [ ]` 条目
- **改目标描述** → 修改 `## 📖 描述` 下面的文字

改完保存即可，系统会读取最新内容来生成每日任务。

### 查看所有目标

```bash
todo goal list
```

## 在 Obsidian 中使用

1. 打开 Obsidian，仓库路径为 `/Users/qbq/Documents/Obsidian Vault`
2. 在左侧文件浏览器找到 `TodoList/` 文件夹
3. 每天查看 `TodoList/Daily/` 下当天日期的文件（如 `2026-03-31.md`）
4. 直接点击复选框勾选已完成的任务
5. 目标文件中的里程碑也可以同样勾选
6. 文件之间通过 `[[韩语学习]]` 等双向链接互相跳转

## 工作流程

1. **设定阶段性目标** → AI 拆解为里程碑
2. **每天 9:05 自动运行** → AI 根据目标和完成情况生成当日任务
3. **在 Obsidian 中勾选完成** → 打开 `TodoList/Daily/` 目录下当天的文件
4. **AI 分析并给建议** → 自动调整后续任务安排

## Obsidian 中的文件结构

```
Obsidian Vault/
└── TodoList/
    ├── Goals/          # 阶段性目标
    ├── Daily/          # 每日 Todo
    ├── Reviews/        # 周报/月报
    └── AI-Suggestions/ # AI 建议记录
```

## 定时任务管理

定时任务通过 macOS launchd 管理，每天 9:05 自动运行。

```bash
# 查看任务状态
launchctl list | grep obsidian-todo

# 手动触发一次
launchctl start com.obsidian-todo-ai.daily

# 停用定时任务
launchctl unload ~/Library/LaunchAgents/com.obsidian-todo-ai.daily.plist

# 重新启用
launchctl load ~/Library/LaunchAgents/com.obsidian-todo-ai.daily.plist
```

## 当前目标

| 目标 | 截止日期 | 描述 |
|------|----------|------|
| 韩语学习 | 2026-09-30 | 从零基础到日常对话，能看懂简单韩剧字幕 |
| 视频剪辑 | 2026-09-30 | 学会视频剪辑，能独立完成 Vlog 和短视频制作 |
