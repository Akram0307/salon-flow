# Reporting Skill

## Overview
Generate comprehensive business reports for salon owners and managers.

## Report Types

| Report | Frequency | Audience |
|--------|-----------|----------|
| Daily Summary | Daily | Manager |
| Weekly Performance | Weekly | Owner |
| Monthly P&L | Monthly | Owner |
| Staff Performance | Weekly | Manager |
| Customer Insights | Monthly | Owner |

## Report Templates

### Daily Summary
```python
def generate_daily_report(salon_id: str, date: str):
    return {
        'title': f'Daily Report - {date}',
        'summary': {
            'totalBookings': 45,
            'completedServices': 42,
            'revenue': 28500
        },
        'staffPerformance': [...],
        'topServices': [...]
    }
```

## Export Formats

- PDF (styled reports)
- Excel (data export)
- CSV (raw data)
- Email (scheduled reports)

## Scheduled Reports
```python
async def schedule_report(salon_id: str, report_type: str, schedule: str):
    task = {
        'salonId': salon_id,
        'reportType': report_type,
        'schedule': schedule,
        'nextRun': calculate_next_run(schedule)
    }
    await db.collection('scheduled_reports').add(task)
```
