"""Obsidian Vault 读写操作模块"""

from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Optional

import yaml
import frontmatter


def load_config() -> dict:
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_vault_path() -> Path:
    config = load_config()
    return Path(config["vault_path"])


def get_todo_root() -> Path:
    config = load_config()
    vault = Path(config["vault_path"])
    todo_root = vault / config["todo_root"]
    todo_root.mkdir(parents=True, exist_ok=True)
    return todo_root


def ensure_directories():
    """确保 Obsidian Vault 中的 TodoList 目录结构存在"""
    root = get_todo_root()
    for subdir in ["Goals", "Daily", "Reviews", "AI-Suggestions"]:
        (root / subdir).mkdir(parents=True, exist_ok=True)


def read_md(filepath: Path) -> frontmatter.Post:
    if not filepath.exists():
        return None
    return frontmatter.load(filepath)


def write_md(filepath: Path, post: frontmatter.Post):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))


def get_daily_path(d: date = None) -> Path:
    if d is None:
        d = date.today()
    return get_todo_root() / "Daily" / f"{d.isoformat()}.md"


def get_goal_path(goal_name: str) -> Path:
    safe_name = goal_name.replace("/", "-").replace("\\", "-")
    return get_todo_root() / "Goals" / f"{safe_name}.md"


def get_review_path(review_type: str, label: str) -> Path:
    return get_todo_root() / "Reviews" / f"{label}.md"


def get_suggestion_path(d: date = None) -> Path:
    if d is None:
        d = date.today()
    return get_todo_root() / "AI-Suggestions" / f"{d.isoformat()}-建议.md"


def list_goals() -> List[Path]:
    goals_dir = get_todo_root() / "Goals"
    if not goals_dir.exists():
        return []
    return sorted(goals_dir.glob("*.md"))


def list_daily_files(last_n: int = 7) -> List[Path]:
    daily_dir = get_todo_root() / "Daily"
    if not daily_dir.exists():
        return []
    files = sorted(daily_dir.glob("*.md"), reverse=True)
    return files[:last_n]


def parse_tasks(content: str) -> List[Dict]:
    """从 Markdown 内容中解析任务列表"""
    tasks = []
    current_priority = "normal"
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("### ") and "高优先级" in stripped:
            current_priority = "high"
        elif stripped.startswith("### ") and "一般优先级" in stripped:
            current_priority = "normal"
        elif stripped.startswith("### ") and "低优先级" in stripped:
            current_priority = "low"
        elif stripped.startswith("- [x] "):
            tasks.append({
                "text": stripped[6:],
                "done": True,
                "priority": current_priority,
            })
        elif stripped.startswith("- [ ] "):
            tasks.append({
                "text": stripped[6:],
                "done": False,
                "priority": current_priority,
            })
    return tasks


def calc_completion_rate(tasks: List[Dict]) -> float:
    if not tasks:
        return 0.0
    done = sum(1 for t in tasks if t["done"])
    return round(done / len(tasks), 2)
