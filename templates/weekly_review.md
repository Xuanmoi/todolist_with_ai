---
type: weekly_review
week: "{{week}}"
generated: "{{generated}}"
---

# 📊 周报 - {{week_label}}

## 📈 每日完成率
| 日期 | 进度条 | 完成率 | 完成/总计 |
|------|--------|--------|-----------|
{{daily_rows}}

## 📊 汇总
- 平均完成率：{{avg_rate}}%
- 总完成任务：{{total_done}}/{{total_tasks}}

## 🎯 目标进展
{{goals_summary}}

## 🤖 AI 周度分析
{{ai_weekly}}
