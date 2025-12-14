from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

from models import App


def _parse_day(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def assign_top_flag(user):
    if user is None:
        return
    apps_by_day = defaultdict(list)
    for app in App.select().where(App.user == user):
        apps_by_day[app.app_day].append(app)

    for day_apps in apps_by_day.values():
        if not day_apps:
            continue
        top_app = max(day_apps, key=lambda app: app.app_time or 0)
        for app in day_apps:
            app.app_top = app == top_app
            app.save()


def build_stats_payload(apps):
    apps = list(apps)
    today = date.today()
    window = [today - timedelta(days=i) for i in range(6, -1, -1)]
    daily_totals = {day: 0 for day in window}

    for app in apps:
        day_val = _parse_day(app.app_day)
        if day_val in daily_totals:
            daily_totals[day_val] += app.app_time or 0

    weekly = {
        'labels': [day.strftime('%m/%d') for day in window],
        'data': [daily_totals[day] for day in window],
    }

    ratio_counter = Counter()
    type_counter = Counter()

    for app in apps:
        time_val = app.app_time or 0
        ratio_counter[app.app_name or '名称未設定'] += time_val
        type_counter[app.app_type or '分類なし'] += time_val

    def _build_counter_payload(counter):
        items = sorted(counter.items(), key=lambda pair: pair[1], reverse=True)
        labels, values = zip(*items) if items else ([], [])
        return {
            'labels': list(labels),
            'data': list(values),
            'total': sum(values) if items else 0,
        }

    ratio = _build_counter_payload(ratio_counter)
    type_ratio = _build_counter_payload(type_counter)

    return {
        'weekly': weekly,
        'ratio': ratio,
        'type': type_ratio,
    }


def top_app(user=None):
    query = App.select().order_by(App.app_time.desc())
    if user is not None:
        query = query.where(App.user == user)
    best = query.first()
    if not best:
        return None
    return {
        'app_id': best.app_id,
        'app_name': best.app_name,
        'app_time': best.app_time,
        'app_day': best.app_day,
        'user_name': best.user.user_name if best.user else None,
    }
