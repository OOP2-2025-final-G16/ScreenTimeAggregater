from datetime import datetime, timedelta

FETCH_DAYS = 7


def _parse_day(app_day):
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


def _normalize_days(days):
    today = datetime.now().date()
    # 直近 `days` 日（本日を含む）をカバーするリストを、古い順で返す。
    # Chart.jsの横軸は古い順で描画されるため、最初の要素は6日前になるよう整形。
    return [today - timedelta(days=i) for i in range(days - 1, -1, -1)]


def weekly_usage(apps):
    days = _normalize_days(FETCH_DAYS)
    usage = {day: 0 for day in days}
    for app in apps:
        parsed = _parse_day(app.app_day)
        if parsed in usage:
            # 関連する日付にだけ app_time を加算（None扱いも0扱いになるよう or 0）
            usage[parsed] += app.app_time or 0
    labels = [day.strftime('%m/%d') for day in days]
    values = [usage[day] for day in days]
    return labels, values


def ratio(apps):
    totals = {}
    for app in apps:
        key = app.app_name or '未設定'
        totals.setdefault(key, 0)
        totals[key] += app.app_time or 0
    if not totals:
        return ['データなし'], [0], 0
    values = list(totals.values())
    # アプリ名をキーとした合計時間のリストを使い、Chart.js のドーナツグラフへ渡す
    return list(totals.keys()), values, sum(values)


def type_ratio(apps):
    totals = {}
    for app in apps:
        key = app.app_type or '未分類'
        totals.setdefault(key, 0)
        totals[key] += app.app_time or 0
    if not totals:
        return ['データなし'], [0], 0
    values = list(totals.values())
    # カテゴリごとの合計時間は typeChart 用のデータセットとなる
    return list(totals.keys()), values, sum(values)
