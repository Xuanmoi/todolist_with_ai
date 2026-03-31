"""每日回顾和报告生成"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List

import frontmatter

from . import vault
from . import todo_manager
from . import goal_manager
from . import ai_advisor


def daily_run(use_ai: bool = True):
    """每日自动运行的主流程：回顾昨天 → AI 生成今天任务 → 写入文件"""
    vault.ensure_directories()
    today = date.today()
    yesterday = today - timedelta(days=1)

    todo_manager.update_daily_summary(yesterday)

    goals_summary = goal_manager.get_goals_summary()
    recent_stats = todo_manager.get_recent_stats(7)

    if use_ai:
        try:
            ai_result = ai_advisor.generate_daily_tasks(goals_summary, recent_stats)
            tasks = ai_result.get("tasks", [])
            suggestion = ai_result.get("suggestion", "")
        except Exception as e:
            tasks = _fallback_tasks()
            suggestion = f"AI 服务暂时不可用（{e}），已使用默认任务。"
    else:
        tasks = _fallback_tasks()
        suggestion = "未启用 AI，使用默认任务模板。"

    related_goals = [g["name"] for g in goal_manager.list_active_goals()]
    filepath = todo_manager.create_daily_todo(today, tasks, related_goals)

    if suggestion:
        _update_ai_suggestion(filepath, suggestion)

    if use_ai:
        _run_review(yesterday, goals_summary, recent_stats)

    return filepath


def _run_review(review_date: date, goals_summary: str, recent_stats: dict):
    """生成 AI 回顾报告"""
    filepath = vault.get_daily_path(review_date)
    post = vault.read_md(filepath)
    if post is None:
        return

    tasks = vault.parse_tasks(post.content)
    if not tasks:
        return

    try:
        review_text = ai_advisor.generate_review(goals_summary, recent_stats, tasks)
    except Exception:
        review_text = "AI 回顾服务暂时不可用。"

    _update_ai_suggestion(filepath, review_text)

    suggestion_path = vault.get_suggestion_path(review_date)
    suggestion_post = frontmatter.Post("")
    suggestion_post.metadata = {
        "date": review_date.isoformat(),
        "type": "daily_review",
    }
    suggestion_post.content = f"""# 🤖 AI 每日回顾 - {review_date.isoformat()}

{review_text}
"""
    vault.write_md(suggestion_path, suggestion_post)


def _update_ai_suggestion(filepath, suggestion: str):
    """更新 Markdown 文件中的 AI 建议区域"""
    post = vault.read_md(filepath)
    if post is None:
        return

    marker = "## 🤖 AI 建议"
    if marker in post.content:
        parts = post.content.split(marker, 1)
        before = parts[0]
        after = parts[1]

        next_section_idx = after.find("\n## ")
        if next_section_idx >= 0:
            remaining = after[next_section_idx:]
        else:
            remaining = ""

        formatted = "\n".join(f"> {line}" for line in suggestion.split("\n"))
        post.content = f"{before}{marker}\n{formatted}\n{remaining}"
        vault.write_md(filepath, post)


def generate_weekly_review():
    """生成每周回顾报告"""
    today = date.today()
    week_num = today.isocalendar()[1]
    year = today.year

    stats = todo_manager.get_recent_stats(7)
    goals_summary = goal_manager.get_goals_summary()

    review_path = vault.get_review_path("weekly", f"{year}-W{week_num:02d}-周报")
    post = frontmatter.Post("")
    post.metadata = {
        "type": "weekly_review",
        "week": f"{year}-W{week_num:02d}",
        "generated": today.isoformat(),
    }

    daily_lines = ""
    for day in stats.get("days", []):
        bar = "█" * int(day["rate"] * 10) + "░" * (10 - int(day["rate"] * 10))
        daily_lines += f"| {day['date']} | {bar} | {int(day['rate'] * 100)}% | {day['done']}/{day['total']} |\n"

    try:
        ai_weekly = ai_advisor.generate_review(goals_summary, stats, [])
    except Exception:
        ai_weekly = "AI 周报服务暂时不可用。"

    post.content = f"""# 📊 周报 - {year}年第{week_num}周

## 📈 每日完成率
| 日期 | 进度条 | 完成率 | 完成/总计 |
|------|--------|--------|-----------|
{daily_lines}
## 📊 汇总
- 平均完成率：{int(stats['avg_rate'] * 100)}%
- 总完成任务：{stats['total_done']}/{stats['total_tasks']}

## 🎯 目标进展
{goals_summary}

## 🤖 AI 周度分析
{ai_weekly}
"""
    vault.write_md(review_path, post)
    return review_path


def _fallback_tasks() -> List[Dict]:
    return [
        {"text": "复习昨日学习内容（30分钟）", "priority": "high"},
        {"text": "推进今日主要学习任务", "priority": "high"},
        {"text": "练习/实操环节", "priority": "normal"},
        {"text": "整理笔记和总结", "priority": "normal"},
    ]
