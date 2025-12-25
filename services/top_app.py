from peewee import fn

from models import App


def top_app(user=None):
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
    # 使用時間合計が最大のアプリを1件だけ取得する
    return query.dicts().first()


def assign_top_flag(user):
    best = top_app(user)
    # まず対象ユーザーのフラグをすべてオフにしておく
    App.update(app_top=False).where(App.user == user).execute()
    if not best or not best.get('name'):
        return
    # もっとも利用されたアプリだけフラグを立てることで ⭐ 表示をひとつに
    App.update(app_top=True).where(
        (App.user == user) & (App.app_name == best['name'])
    ).execute()
