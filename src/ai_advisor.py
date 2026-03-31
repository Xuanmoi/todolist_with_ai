"""DeepSeek AI 建议引擎"""

from __future__ import annotations

import json
from datetime import date
from typing import Dict, List

from openai import OpenAI

from . import vault
from . import goal_manager
from . import todo_manager


def get_client() -> OpenAI:
    config = vault.load_config()
    ai_config = config.get("ai", {})
    return OpenAI(
        api_key=ai_config.get("api_key", ""),
        base_url=ai_config.get("base_url", "https://api.deepseek.com"),
    )


def get_model() -> str:
    config = vault.load_config()
    return config.get("ai", {}).get("model", "deepseek-chat")


SYSTEM_PROMPT = """你是一个专业的个人效率教练和目标管理助手。你的任务是：
1. 根据用户的阶段性目标，拆解出具体的每日可执行任务
2. 分析用户的任务完成情况，发现模式和问题
3. 给出具体、可操作的建议来提高效率
4. 动态调整任务安排，确保目标按时完成

你的建议应该：
- 具体而非笼统
- 考虑用户的实际完成能力（基于历史数据）
- 平衡多个目标之间的时间分配
- 鼓励正向反馈，避免过度批评

回复请使用中文。"""


def generate_daily_tasks(goals_summary: str, recent_stats: Dict) -> Dict:
    """基于目标和近期完成情况，AI 生成今日任务"""
    client = get_client()

    stats_text = _format_stats(recent_stats)

    prompt = f"""请根据以下信息，为今天({date.today().isoformat()})生成每日任务清单。

## 当前阶段性目标
{goals_summary}

## 近期完成统计
{stats_text}

请以 JSON 格式返回任务列表，格式如下：
```json
{{
  "tasks": [
    {{"text": "任务描述", "priority": "high"}},
    {{"text": "任务描述", "priority": "normal"}}
  ],
  "suggestion": "今日整体建议（1-3句话）"
}}
```

注意：
- 高优先级任务 2-3 个，普通任务 2-3 个
- 每个任务应该是今天可以完成的具体行动
- 任务应该推动阶段性目标的进展
- 根据近期完成率动态调整任务数量和难度"""

    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    content = response.choices[0].message.content
    return _parse_tasks_response(content)


def generate_review(goals_summary: str, recent_stats: Dict, today_tasks: List[Dict]) -> str:
    """生成每日回顾和建议"""
    client = get_client()

    stats_text = _format_stats(recent_stats)
    tasks_text = _format_tasks(today_tasks)

    prompt = f"""请根据以下信息进行每日回顾，给出建议。

## 当前阶段性目标
{goals_summary}

## 近期完成统计
{stats_text}

## 今日任务完成情况
{tasks_text}

请给出：
1. 对今天完成情况的简要点评（2-3句）
2. 发现的模式或问题（如果有）
3. 对明天的具体建议（2-3条）
4. 鼓励的话（1句）

请直接用自然语言回复，不需要 JSON 格式。"""

    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content


def decompose_goal(goal_name: str, goal_description: str) -> List[str]:
    """AI 将阶段性目标拆解为里程碑"""
    client = get_client()

    prompt = f"""请将以下阶段性目标拆解为 5-8 个具体的里程碑（按时间顺序排列）。

目标名称：{goal_name}
目标描述：{goal_description}

请以 JSON 格式返回：
```json
{{
  "milestones": [
    "里程碑1描述",
    "里程碑2描述"
  ]
}}
```

每个里程碑应该是可衡量的、具体的阶段性成果。"""

    response = client.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    content = response.choices[0].message.content
    return _parse_milestones_response(content)


def _format_stats(stats: dict) -> str:
    if not stats.get("days"):
        return "暂无历史数据（首次使用）"

    lines = [f"近 {len(stats['days'])} 天平均完成率：{int(stats['avg_rate'] * 100)}%\n"]
    for day in stats["days"]:
        lines.append(f"  {day['date']}: {int(day['rate'] * 100)}% ({day['done']}/{day['total']})")
    return "\n".join(lines)


def _format_tasks(tasks: List[Dict]) -> str:
    if not tasks:
        return "今天暂无任务记录"
    lines = []
    for t in tasks:
        status = "✅" if t["done"] else "❌"
        lines.append(f"  {status} [{t['priority']}] {t['text']}")
    return "\n".join(lines)


def _parse_tasks_response(content: str) -> dict:
    """解析 AI 返回的任务 JSON"""
    try:
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            data = json.loads(content[json_start:json_end])
            return data
    except (json.JSONDecodeError, ValueError):
        pass
    return {
        "tasks": [
            {"text": "复习昨日学习内容", "priority": "high"},
            {"text": "按计划推进今日学习任务", "priority": "high"},
            {"text": "整理学习笔记", "priority": "normal"},
        ],
        "suggestion": "AI 返回格式异常，已使用默认任务。请检查 API 配置。",
    }


def _parse_milestones_response(content: str) -> List[str]:
    """解析 AI 返回的里程碑 JSON"""
    try:
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            data = json.loads(content[json_start:json_end])
            return data.get("milestones", [])
    except (json.JSONDecodeError, ValueError):
        pass
    return ["（AI 解析失败，请手动添加里程碑）"]
