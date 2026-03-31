"""阶段性目标管理"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

import frontmatter

from . import vault


def create_goal(name: str, description: str, deadline: str = None,
                milestones: List[str] = None) -> Path:
    """创建阶段性目标文件"""
    filepath = vault.get_goal_path(name)

    post = frontmatter.Post("")
    post.metadata = {
        "name": name,
        "created": date.today().isoformat(),
        "deadline": deadline or "",
        "status": "active",
    }

    milestone_text = ""
    if milestones:
        milestone_text = "\n".join(f"- [ ] {m}" for m in milestones)
    else:
        milestone_text = "- [ ] （等待 AI 拆解...）"

    post.content = f"""# 🎯 {name}

## 📖 描述
{description}

## 📅 时间规划
- 创建日期：{date.today().isoformat()}
- 截止日期：{deadline or '待定'}

## 🏁 里程碑
{milestone_text}

## 📊 进度追踪
- 当前进度：0%
- 状态：进行中

## 📝 备注
"""
    vault.write_md(filepath, post)
    return filepath


def get_goal(name: str) -> Optional[frontmatter.Post]:
    filepath = vault.get_goal_path(name)
    return vault.read_md(filepath)


def list_active_goals() -> List[Dict]:
    """列出所有活跃目标"""
    goals = []
    for path in vault.list_goals():
        post = vault.read_md(path)
        if post and post.metadata.get("status") == "active":
            goals.append({
                "name": post.metadata.get("name", path.stem),
                "path": path,
                "content": post.content,
                "metadata": post.metadata,
            })
    return goals


def get_goals_summary() -> str:
    """获取所有目标的摘要文本，用于发送给 AI"""
    goals = list_active_goals()
    if not goals:
        return "当前没有活跃的目标。"

    summary_parts = []
    for g in goals:
        tasks = vault.parse_tasks(g["content"])
        done = sum(1 for t in tasks if t["done"])
        total = len(tasks)
        summary_parts.append(
            f"【{g['name']}】\n"
            f"  里程碑进度：{done}/{total}\n"
            f"  内容：\n{g['content']}\n"
        )
    return "\n---\n".join(summary_parts)


def update_goal_progress(name: str):
    """根据里程碑勾选情况更新目标进度"""
    filepath = vault.get_goal_path(name)
    post = vault.read_md(filepath)
    if post is None:
        return

    tasks = vault.parse_tasks(post.content)
    rate = vault.calc_completion_rate(tasks)

    old_marker = "## 📊 进度追踪"
    if old_marker in post.content:
        before = post.content.split(old_marker)[0]
        status = "已完成" if rate >= 1.0 else "进行中"
        after_parts = post.content.split(old_marker, 1)[1]
        next_section = ""
        for line in after_parts.split("\n"):
            if line.startswith("## ") and "进度追踪" not in line:
                idx = after_parts.index(line)
                next_section = after_parts[idx:]
                break

        post.content = before + f"""{old_marker}
- 当前进度：{int(rate * 100)}%
- 状态：{status}

{next_section}"""

    vault.write_md(filepath, post)
