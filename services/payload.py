from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Iterable, List


def _to_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return None
    return None


def _int(value: Any) -> int:
    try:
        return max(int(value), 0)
    except (TypeError, ValueError):
        return 0


def _build_ranking(source: defaultdict[str, int]) -> List[dict[str, Any]]:
    items = sorted(source.items(), key=lambda item: item[1], reverse=True)
    return [{'label': label, 'total': total} for label, total in items if total > 0]


def build_stats_payload(apps: Iterable[Any]) -> dict[str, Any]:
    """Aggregate data for the statistics charts."""
    totals_by_day: defaultdict[date, int] = defaultdict(int)
    totals_by_app: defaultdict[str, int] = defaultdict(int)
    totals_by_type: defaultdict[str, int] = defaultdict(int)
    total_usage = 0

    for app in apps:
        time_spent = _int(getattr(app, 'app_time', 0))
        total_usage += time_spent

        app_day = _to_date(getattr(app, 'app_day', None))
        if app_day:
            totals_by_day[app_day] += time_spent

        app_name = getattr(app, 'app_name', None) or '名称未設定'
        totals_by_app[app_name] += time_spent

        app_type = getattr(app, 'app_type', None) or '未分類'
        totals_by_type[app_type] += time_spent

    today = date.today()
    weekly: List[dict[str, Any]] = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        weekly.append({'label': day.strftime('%Y-%m-%d'), 'total': totals_by_day.get(day, 0)})

    return {
        'weekly': weekly,
        'app_ratios': _build_ranking(totals_by_app),
        'type_ratios': _build_ranking(totals_by_type),
        'total_usage': total_usage,
    }
