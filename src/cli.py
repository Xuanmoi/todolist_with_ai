"""CLI 入口 - 所有命令的统一接口"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from datetime import date

from . import vault
from . import todo_manager
from . import goal_manager
from . import ai_advisor
from . import daily_review

console = Console()


@click.group()
def cli():
    """📋 Obsidian Todo AI - 智能 TodoList 管理系统"""
    vault.ensure_directories()


# ──────────────────────────────────────────────
#  每日运行
# ──────────────────────────────────────────────

@cli.command("daily-run")
@click.option("--no-ai", is_flag=True, help="不使用 AI 生成任务")
def cmd_daily_run(no_ai):
    """🚀 每日自动运行（回顾昨天 + 生成今天任务）"""
    with console.status("[bold green]正在生成今日任务..."):
        filepath = daily_review.daily_run(use_ai=not no_ai)
    console.print(f"[green]✅ 今日 Todo 已生成：[/green]{filepath}")
    _show_today()


@cli.command("today")
def cmd_today():
    """📋 查看今日 Todo"""
    _show_today()


def _show_today():
    filepath = vault.get_daily_path()
    post = vault.read_md(filepath)
    if post is None:
        console.print("[yellow]⚠️ 今日 Todo 尚未生成，请先运行 [bold]todo daily-run[/bold][/yellow]")
        return

    tasks = vault.parse_tasks(post.content)
    rate = vault.calc_completion_rate(tasks)

    table = Table(title=f"📋 {date.today().isoformat()} Todo", box=box.ROUNDED)
    table.add_column("状态", width=4)
    table.add_column("优先级", width=8)
    table.add_column("任务", min_width=30)

    for t in tasks:
        status = "✅" if t["done"] else "⬜"
        priority = "🔴 高" if t["priority"] == "high" else "🔵 普通"
        style = "dim" if t["done"] else ""
        table.add_row(status, priority, t["text"], style=style)

    console.print(table)
    console.print(f"\n完成率：[bold]{int(rate * 100)}%[/bold]")


# ──────────────────────────────────────────────
#  目标管理
# ──────────────────────────────────────────────

@cli.group("goal")
def cmd_goal():
    """🎯 阶段性目标管理"""
    pass


@cmd_goal.command("add")
@click.argument("name")
@click.option("--desc", "-d", prompt="目标描述", help="目标详细描述")
@click.option("--deadline", help="截止日期 (YYYY-MM-DD)")
@click.option("--ai-decompose", is_flag=True, default=True, help="使用 AI 拆解里程碑")
def cmd_goal_add(name, desc, deadline, ai_decompose):
    """添加新的阶段性目标"""
    milestones = None
    if ai_decompose:
        with console.status("[bold green]AI 正在拆解目标为里程碑..."):
            try:
                milestones = ai_advisor.decompose_goal(name, desc)
                console.print(f"[green]✅ AI 成功生成 {len(milestones)} 个里程碑[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️ AI 拆解失败（{e}），将创建空白里程碑[/yellow]")

    filepath = goal_manager.create_goal(name, desc, deadline, milestones)
    console.print(f"[green]✅ 目标已创建：[/green]{filepath}")

    if milestones:
        for i, m in enumerate(milestones, 1):
            console.print(f"  {i}. {m}")


@cmd_goal.command("list")
def cmd_goal_list():
    """查看所有活跃目标"""
    goals = goal_manager.list_active_goals()
    if not goals:
        console.print("[yellow]暂无活跃目标，使用 [bold]todo goal add[/bold] 添加[/yellow]")
        return

    for g in goals:
        tasks = vault.parse_tasks(g["content"])
        done = sum(1 for t in tasks if t["done"])
        total = len(tasks)
        rate = done / total * 100 if total > 0 else 0

        panel = Panel(
            f"📊 里程碑进度：{done}/{total} ({int(rate)}%)\n"
            f"📅 截止日期：{g['metadata'].get('deadline', '待定')}",
            title=f"🎯 {g['name']}",
            border_style="green" if rate >= 80 else "yellow" if rate >= 50 else "red",
        )
        console.print(panel)


# ──────────────────────────────────────────────
#  任务操作
# ──────────────────────────────────────────────

@cli.command("add")
@click.argument("text")
@click.option("--priority", "-p", type=click.Choice(["high", "normal"]), default="normal")
def cmd_add(text, priority):
    """➕ 添加临时任务到今日 Todo"""
    todo_manager.add_task(text, priority)
    console.print(f"[green]✅ 已添加任务：[/green]{text}")


# ──────────────────────────────────────────────
#  统计和回顾
# ──────────────────────────────────────────────

@cli.command("stats")
@click.option("--days", "-n", default=7, help="统计天数")
def cmd_stats(days):
    """📊 查看完成情况统计"""
    stats = todo_manager.get_recent_stats(days)

    if not stats["days"]:
        console.print("[yellow]暂无历史数据[/yellow]")
        return

    table = Table(title=f"📊 近 {days} 天完成统计", box=box.ROUNDED)
    table.add_column("日期", width=12)
    table.add_column("进度条", width=12)
    table.add_column("完成率", width=8)
    table.add_column("完成/总计", width=10)

    for day in stats["days"]:
        bar_filled = int(day["rate"] * 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        rate_str = f"{int(day['rate'] * 100)}%"
        count = f"{day['done']}/{day['total']}"

        if day["rate"] >= 0.8:
            style = "green"
        elif day["rate"] >= 0.5:
            style = "yellow"
        else:
            style = "red"

        table.add_row(day["date"], bar, rate_str, count, style=style)

    console.print(table)
    console.print(f"\n平均完成率：[bold]{int(stats['avg_rate'] * 100)}%[/bold]")
    console.print(f"总计完成：[bold]{stats['total_done']}/{stats['total_tasks']}[/bold]")


@cli.command("review")
def cmd_review():
    """🤖 触发 AI 回顾分析"""
    with console.status("[bold green]AI 正在分析..."):
        goals_summary = goal_manager.get_goals_summary()
        recent_stats = todo_manager.get_recent_stats(7)

        post = vault.read_md(vault.get_daily_path())
        today_tasks = vault.parse_tasks(post.content) if post else []

        try:
            review_text = ai_advisor.generate_review(goals_summary, recent_stats, today_tasks)
        except Exception as e:
            console.print(f"[red]❌ AI 回顾失败：{e}[/red]")
            return

    console.print(Panel(review_text, title="🤖 AI 回顾分析", border_style="cyan"))


@cli.command("weekly")
def cmd_weekly():
    """📊 生成每周回顾报告"""
    with console.status("[bold green]正在生成周报..."):
        filepath = daily_review.generate_weekly_review()
    console.print(f"[green]✅ 周报已生成：[/green]{filepath}")


@cli.command("init")
def cmd_init():
    """🔧 初始化项目（创建目录结构）"""
    vault.ensure_directories()
    console.print("[green]✅ 目录结构已创建[/green]")
    root = vault.get_todo_root()
    console.print(f"  📁 {root}/Goals/")
    console.print(f"  📁 {root}/Daily/")
    console.print(f"  📁 {root}/Reviews/")
    console.print(f"  📁 {root}/AI-Suggestions/")


if __name__ == "__main__":
    cli()
