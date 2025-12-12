from .user import user_bp
from .app import (
    app_day_bp,
    app_id_bp,
    app_name_bp,
    app_time_bp,
    app_top_bp,
    app_type_bp,
    app_user_bp,
)

# Blueprintをリストとしてまとめる
blueprints = [
    user_bp,
    app_id_bp,
    app_type_bp,
    app_name_bp,
    app_time_bp,
    app_day_bp,
    app_top_bp,
    app_user_bp,
]
