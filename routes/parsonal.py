from datetime import datetime

from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from models import App, User
from services.statistics import (
    assign_top_flag,
    build_stats_payload,
    top_app,
)

personal_bp = Blueprint('personal', __name__, url_prefix='/personal')


def _current_user():
    """セッションからユーザーIDを取り出し、ユーザーを返す。"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.get_or_none(User.user_id == user_id)





@personal_bp.route('/')
def dashboard():
    """ログインユーザーのダッシュボードを表示する。"""
    user = _current_user()
    if not user:
        flash('ログインが必要です。', 'error')
        return redirect(url_for('index'))
    apps = App.select().where(App.user == user).order_by(App.app_day.desc(), App.app_time.desc())
    return render_template('personal_dashboard.html', user=user, apps=apps)


@personal_bp.route('/apps/add', methods=['POST'])
def add_app():
    """フォームからアプリを登録し、トップフラグを再計算する。"""
    user = _current_user()
    if not user:
        return redirect(url_for('index'))
    app_type = request.form.get('app_type', '').strip()
    app_name = request.form.get('app_name', '').strip()
    app_time = request.form.get('app_time', '0')
    app_day = request.form.get('app_day', '').strip()
    app_top = request.form.get('app_top') == 'on'
    try:
        app_time = int(app_time)
    except ValueError:
        app_time = 0
    App.create(
        user=user,
        app_type=app_type or '未分類',
        app_name=app_name or '名称未設定',
        app_time=app_time,
        app_day=app_day or datetime.now().strftime('%Y-%m-%d'),
        app_top=app_top,
    )
    flash('アプリ情報を登録しました。', 'info')
    assign_top_flag(user)
    return redirect(url_for('personal.dashboard'))


@personal_bp.route('/apps/<int:app_id>/edit', methods=['GET', 'POST'])
def edit_app(app_id):
    """アプリ情報を編集し、トップフラグを再計算する。"""
    user = _current_user()
    if not user:
        return redirect(url_for('index'))
    app = App.get_or_none(App.app_id == app_id, App.user == user)
    if not app:
        abort(404)
    if request.method == 'POST':
        app.app_type = request.form.get('app_type', app.app_type)
        app.app_name = request.form.get('app_name', app.app_name)
        app.app_day = request.form.get('app_day', app.app_day)
        try:
            app.app_time = int(request.form.get('app_time', app.app_time))
        except ValueError:
            pass
        app.app_top = request.form.get('app_top') == 'on'
        app.save()
        assign_top_flag(user)
        flash('アプリ情報を更新しました。', 'info')
        return redirect(url_for('personal.dashboard'))
    return render_template('app_edit.html', app=app)


@personal_bp.route('/apps/<int:app_id>/delete', methods=['POST'])
def delete_app(app_id):
    """アプリを削除し、トップアプリフラグを再設定する。"""
    user = _current_user()
    if not user:
        return redirect(url_for('index'))
    app = App.get_or_none(App.app_id == app_id, App.user == user)
    if not app:
        abort(404)
    app.delete_instance()
    assign_top_flag(user)
    flash('アプリを削除しました。', 'info')
    return redirect(url_for('personal.dashboard'))


@personal_bp.route('/stats')
def personal_stats():
    """個人集計ページのテンプレートを表示する。"""
    user = _current_user()
    if not user:
        return redirect(url_for('index'))
    return render_template(
        'stats.html',
        title='個人集計',
        user=user,
        stats_endpoint=url_for('personal.personal_stats_data'),
        other_url=url_for('personal.global_stats'),
        other_label='全体集計へ',
    )


@personal_bp.route('/stats/global')
def global_stats():
    """全体集計ページのテンプレートを表示する。"""
    return render_template(
        'stats.html',
        title='全体集計',
        user=None,
        stats_endpoint=url_for('personal.global_stats_data'),
        other_url=url_for('personal.personal_stats'),
        other_label='個人集計へ',
    )


@personal_bp.route('/stats/data')
def personal_stats_data():
    """個人集計データをJSONで返すAPI。"""
    user = _current_user()
    if not user:
        return jsonify({'error': 'ログインが必要です。'}), 401
    apps = list(App.select().where(App.user == user))
    payload = build_stats_payload(apps)
    payload['top_app'] = top_app(user)
    return jsonify(payload)


@personal_bp.route('/stats/global/data')
def global_stats_data():
    """全体集計データをJSONで返すAPI。"""
    apps = list(App.select())
    payload = build_stats_payload(apps)
    payload['top_app'] = top_app()
    return jsonify(payload)
