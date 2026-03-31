"""Todo 管理核心逻辑"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import frontmatter

from . import vault


def create_daily_todo(d: date = None, tasks: List[Dict] = None, related_goals: List[str] = None) -> Path:
    """创建每日 Todo 文件，如已存在则跳过"""
    if d is None:
        d = date.today()
    filepath = vault.get_daily_path(d)

    if filepath.exists():
        return filepath

    if related_goals is None:
        related_goals = [p.stem for p in vault.list_goals()]

    post = frontmatter.Post("")
    post.metadata = {
        "date": d.isoformat(),
        "related_goals": related_goals,
        "ai_reviewed": False,
        "completion_rate": 0.0,
    }

    goal_links = "\n".join(f"- [[{g}]]" for g in related_goals) if related_goals else "- 暂无"

    high_tasks = ""
    normal_tasks = ""
    if tasks:
        for t in tasks:
            line = f"- [ ] {t['text']}\n"
            if t.get("priority") == "high":
                high_tasks += line
            else:
                normal_tasks += line

    if not high_tasks:
        high_tasks = "- [ ] （等待 AI 生成...）\n"
    if not normal_tasks:
        normal_tasks = "- [ ] （等待 AI 生成...）\n"

    post.content = f"""# 📋 {d.isoformat()} Todo

## 🎯 关联目标
{goal_links}

## 📝 任务列表

### 高优先级
{high_tasks.rstrip()}

### 一般优先级
{normal_tasks.rstrip()}

## 🤖 AI 建议
> 暂无

## 📊 今日小结
- 完成率：0%
- 状态：进行中
"""
    vault.write_md(filepath, post)
    return filepath


def update_daily_summary(d: date = None):
    """根据勾选状态更新每日小结"""
    if d is None:
        d = date.today()
    filepath = vault.get_daily_path(d)
    post = vault.read_md(filepath)
    if post is None:
        return

    tasks = vault.parse_tasks(post.content)
    rate = vault.calc_completion_rate(tasks)
    post.metadata["completion_rate"] = rate
    done_count = sum(1 for t in tasks if t["done"])
    total = len(tasks)

    old_summary_marker = "## 📊 今日小结"
    if old_summary_marker in post.content:
        before = post.content.split(old_summary_marker)[0]
        status = "已完成" if rate >= 1.0 else "进行中"
        post.content = before + f"""{old_summary_marker}
- 完成率：{int(rate * 100)}% ({done_count}/{total})
- 状态：{status}
"""
    vault.write_md(filepath, post)


def add_task(text: str, priority: str = "normal", d: date = None):
    """向今日 Todo 添加任务"""
    if d is None:
        d = date.today()
    filepath = vault.get_daily_path(d)
    post = vault.read_md(filepath)
    if post is None:
        create_daily_todo(d)
        post = vault.read_md(filepath)

    marker = "### 高优先级" if priority == "high" else "### 一般优先级"
    lines = post.content.split("\n")
    new_lines = []
    inserted = False
    for i, line in enumerate(lines):
        new_lines.append(line)
        if line.strip() == marker and not inserted:
            placeholder = "- [ ] （等待 AI 生成...）"
            remaining = lines[i + 1:] if i + 1 < len(lines) else []
            has_placeholder = any(placeholder in l for l in remaining[:3])

            if has_placeholder:
                for j in range(i + 1, min(i + 4, len(lines))):
                    if placeholder in lines[j]:
                        lines[j] = f"- [ ] {text}"
                        new_lines = lines[:i + 1] + lines[i + 1:]
                        inserted = True
                        break
            if not inserted:
                new_lines.append(f"- [ ] {text}")
                inserted = True

    if not inserted:
        new_lines.append(f"- [ ] {text}")

    post.content = "\n".join(new_lines)
    vault.write_md(filepath, post)


def get_recent_stats(days: int = 7) -> dict:
    """获取近 N 天的完成统计"""
    stats = {"days": [], "avg_rate": 0.0, "total_done": 0, "total_tasks": 0}
    today = date.today()

    for i in range(days):
        d = today - timedelta(days=i)
        filepath = vault.get_daily_path(d)
        post = vault.read_md(filepath)
        if post is None:
            continue
        tasks = vault.parse_tasks(post.content)
        rate = vault.calc_completion_rate(tasks)
        done = sum(1 for t in tasks if t["done"])
        total = len(tasks)
        stats["days"].append({
            "date": d.isoformat(),
            "rate": rate,
            "done": done,
            "total": total,
        })
        stats["total_done"] += done
        stats["total_tasks"] += total

    if stats["total_tasks"] > 0:
        stats["avg_rate"] = round(stats["total_done"] / stats["total_tasks"], 2)
    return stats
