from typing import Optional

from models.app import App
from models.db import db
from models.user import User


def _serialize(app: App) -> dict[str, str | int]:
    return {
        'app_id': app.app_id,
        'app_name': app.app_name,
        'app_type': app.app_type,
        'app_time': app.app_time,
        'app_day': app.app_day,
    }


def assign_top_flag(user: Optional[User]) -> None:
    if not user:
        return

    db.connect(reuse_if_open=True)
    try:
        App.update(app_top=False).where(App.user == user).execute()
        top = (
            App.select()
            .where(App.user == user)
            .order_by(App.app_time.desc(), App.app_day.desc())
            .first()
        )
        if top:
            top.app_top = True
            top.save()
    finally:
        db.close()


def top_app(user: Optional[User] = None) -> Optional[dict[str, str | int]]:
    db.connect(reuse_if_open=True)
    try:
        query = App.select()
        if user:
            query = query.where(App.user == user)
        top = query.order_by(App.app_time.desc(), App.app_day.desc()).first()
        if not top:
            return None
        return _serialize(top)
    finally:
        db.close()
