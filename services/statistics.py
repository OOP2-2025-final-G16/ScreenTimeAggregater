from datetime import datetime, timedelta

from peewee import fn

from models import App


def weekly_usage(apps):
    """日別の利用時間ラベルと値を返す"""
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    usage = {day: 0 for day in days}
    for app in apps:
        parsed = _parse_day(app.app_day)
        if parsed in usage:
            usage[parsed] += app.app_time or 0
    labels = [day.strftime('%m/%d') for day in days]
    values = [usage[day] for day in days]
    return labels, values


def ratio(apps):
    """アプリ名ごとの利用時間比率を算出"""
    totals = {}
    for app in apps:
        key = app.app_name or '未設定'
        totals.setdefault(key, 0)
        totals[key] += app.app_time or 0
    if not totals:
        return ['データなし'], [0], 0
    values = list(totals.values())
    return list(totals.keys()), values, sum(values)


def type_ratio(apps):
    """カテゴリごとの利用時間比率を算出"""
    totals = {}
    for app in apps:
        key = app.app_type or '未分類'
        totals.setdefault(key, 0)
        totals[key] += app.app_time or 0
    if not totals:
        return ['データなし'], [0], 0
    values = list(totals.values())
    return list(totals.keys()), values, sum(values)


def top_app(user=None):
    """指定ユーザーまたは全体で使用時間が最も長いアプリを返す"""
    query = (
        App.select(
            App.app_name.alias('name'),
            fn.COALESCE(fn.SUM(App.app_time), 0).alias('time'),
        )
        .group_by(App.app_name)
        .order_by(fn.SUM(App.app_time).desc())
        .limit(1)
    )
    if user:
        query = query.where(App.user == user)
    result = query.dicts().first()
    if not result:
        return None
    return result


def assign_top_flag(user):
    """対象ユーザーのトップアプリフラグを更新"""
    best = top_app(user)
    App.update(app_top=False).where(App.user == user).execute()
    if not best or not best.get('name'):
        return
    App.update(app_top=True).where(
        (App.user == user) & (App.app_name == best['name'])
    ).execute()


def build_stats_payload(apps):
    """統計チャートで使う JSON ペイロードを生成"""
    weekly_labels, weekly_values = weekly_usage(apps)
    ratio_labels, ratio_values, ratio_total = ratio(apps)
    type_labels, type_values, type_total = type_ratio(apps)
    return {
        'weekly_labels': weekly_labels,
        'weekly_values': weekly_values,
        'ratio_labels': ratio_labels,
        'ratio_values': ratio_values,
        'ratio_total': ratio_total,
        'type_labels': type_labels,
        'type_values': type_values,
        'type_total': type_total,
    }


def _parse_day(app_day):
    """多形式の日付文字列を datetime.date に変換"""
    if not app_day:
        return None
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y'):
        try:
            return datetime.strptime(app_day, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(app_day).date()
    except ValueError:
        return None