"""初始化预设的阶段性目标（不依赖 AI，可离线运行）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import vault
from src import goal_manager


def init():
    vault.ensure_directories()

    goal_manager.create_goal(
        name="韩语学习",
        description="系统学习韩语，从零基础到能进行日常对话，能看懂简单的韩剧字幕。",
        deadline="2026-09-30",
        milestones=[
            "掌握韩语字母表（元音+辅音）和基本发音规则",
            "学会 100 个常用单词和基础问候语",
            "掌握基本语法结构（主语+宾语+动词）",
            "能进行简单的自我介绍和日常对话",
            "学会数字、时间、日期的表达",
            "能看懂简单的韩语文章和短消息",
            "能听懂韩剧中的基础日常对话",
        ],
    )

    goal_manager.create_goal(
        name="视频剪辑",
        description="学习视频剪辑技术，能独立完成 Vlog、短视频等内容的制作和后期处理。",
        deadline="2026-09-30",
        milestones=[
            "熟悉剪辑软件基本界面和操作（如 DaVinci Resolve / Premiere Pro）",
            "掌握基础剪辑技巧：剪切、拼接、转场",
            "学会音频处理：配乐、降噪、音量调节",
            "掌握字幕添加和基础文字动画",
            "学会调色基础和画面风格统一",
            "独立完成一个完整的 Vlog 作品",
            "掌握短视频（抖音/B站）格式和节奏",
        ],
    )

    print("✅ 阶段性目标已初始化：")
    for p in vault.list_goals():
        print(f"  📁 {p}")


if __name__ == "__main__":
    init()
