import os
from datetime import datetime

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from models import App, User, initialize_database
from services.statistics import assign_top_flag, build_stats_payload, top_app

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-this-secret')

# データベースの初期化
initialize_database()


def _current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.get_or_none(User.user_id == user_id)


def _serialize_app(app_obj):
    return {
        'app_id': app_obj.app_id,
        'app_name': app_obj.app_name,
        'app_type': app_obj.app_type,
        'app_time': app_obj.app_time,
        'app_day': app_obj.app_day,
        'app_top': bool(app_obj.app_top),
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_name = request.form.get('user_name', '').strip()
        user_password = request.form.get('user_password', '').strip()
        user = User.get_or_none(
            (User.user_name == user_name) & (User.user_password == user_password)
        )
        if user:
            session['user_id'] = user.user_id
            return redirect(url_for('stats_personal'))
        flash('ユーザー名またはパスワードが正しくありません。', 'error')
    return render_template('index.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    payload = request.get_json(silent=True) or {}
    user_name = payload.get('user_name', '').strip()
    user_password = payload.get('user_password', '').strip()
    if not user_name or not user_password:
        return jsonify({'error': 'ユーザー名とパスワードは必須です。'}), 400
    user = User.get_or_none(
        (User.user_name == user_name) & (User.user_password == user_password)
    )
    if not user:
        return jsonify({'error': 'ユーザー名またはパスワードが正しくありません。'}), 401
    session['user_id'] = user.user_id
    return jsonify({'success': True, 'redirect': url_for('stats_personal')}), 200


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('ログアウトしました。', 'info')
    return redirect(url_for('index'))


def _get_user_apps(user):
    return (
        App.select()
        .where(App.user == user)
        .order_by(App.app_day.desc(), App.app_time.desc())
    )


@app.route('/personal')
def personal():
    user = _current_user()
    if not user:
        flash('ログインが必要です。', 'error')
        return redirect(url_for('index'))
    apps = list(_get_user_apps(user))
    return render_template('personal_dashboard.html', user=user, apps=apps)


@app.route('/personal/apps/add', methods=['POST'])
def personal_add_app():
    user = _current_user()
    if not user:
        flash('ログインが必要です。', 'error')
        return redirect(url_for('index'))

    app_name = request.form.get('app_name', '').strip() or '名称未設定'
    app_type = request.form.get('app_type', '').strip() or '未分類'
    app_time_raw = request.form.get('app_time', 0)
    try:
        app_time = int(app_time_raw)
    except (TypeError, ValueError):
        app_time = 0
    app_day = request.form.get('app_day', '').strip()
    if not app_day:
        app_day = datetime.now().strftime('%Y-%m-%d')

    App.create(
        user=user,
        app_name=app_name,
        app_type=app_type,
        app_time=app_time,
        app_day=app_day,
        app_top=False,
    )
    flash('アプリ情報を登録しました。', 'info')
    assign_top_flag(user)
    return redirect(url_for('personal'))


@app.route('/personal/apps/<int:app_id>/delete', methods=['POST'])
def personal_delete_app(app_id):
    user = _current_user()
    if not user:
        flash('ログインが必要です。', 'error')
        return redirect(url_for('index'))
    app_obj = App.get_or_none(App.app_id == app_id, App.user == user)
    if not app_obj:
        flash('指定したアプリが見つかりません。', 'error')
        return redirect(url_for('personal'))
    app_obj.delete_instance()
    assign_top_flag(user)
    flash('アプリを削除しました。', 'info')
    return redirect(url_for('personal'))


@app.route('/users')
def users():
    users = list(User.select().order_by(User.user_name))
    return render_template('user_list.html', title='ユーザー一覧', items=users)


@app.route('/users/add', methods=['GET', 'POST'])
def users_add():
    if request.method == 'POST':
        user_name = request.form.get('user_name', '').strip()
        user_password = request.form.get('user_password', '').strip()
        if not user_name or not user_password:
            flash('ユーザー名とパスワードは必須です。', 'error')
            return render_template('user_add.html')
        existing = User.get_or_none(User.user_name == user_name)
        if existing:
            flash('そのユーザー名は既に使われています。', 'error')
            return render_template('user_add.html')
        User.create(user_name=user_name, user_password=user_password)
        flash('ユーザーを追加しました。', 'info')
        return redirect(url_for('users'))
    return render_template('user_add.html')


@app.route('/api/personal/apps', methods=['GET', 'POST'])
def api_personal_apps():
    user = _current_user()
    if not user:
        return jsonify({'error': 'ログインが必要です。'}), 401

    if request.method == 'GET':
        apps = (
            App.select()
            .where(App.user == user)
            .order_by(App.app_day.desc(), App.app_time.desc())
        )
        return jsonify([_serialize_app(app_obj) for app_obj in apps])

    payload = request.get_json(silent=True) or {}
    app_type = payload.get('app_type', '').strip() or '未分類'
    app_name = payload.get('app_name', '').strip() or '名称未設定'
    app_time = payload.get('app_time', 0)
    app_day = payload.get('app_day', '').strip()
    app_top = payload.get('app_top', False)
    try:
        app_time = int(app_time)
    except (TypeError, ValueError):
        app_time = 0
    if not app_day:
        app_day = datetime.now().strftime('%Y-%m-%d')
    app_obj = App.create(
        user=user,
        app_type=app_type,
        app_name=app_name,
        app_time=app_time,
        app_day=app_day,
        app_top=bool(app_top),
    )
    flash('アプリ情報を登録しました。', 'info')
    assign_top_flag(user)
    return jsonify(_serialize_app(app_obj)), 201


@app.route('/api/personal/apps/<int:app_id>', methods=['PUT', 'DELETE'])
def api_personal_app_detail(app_id):
    user = _current_user()
    if not user:
        return jsonify({'error': 'ログインが必要です。'}), 401
    app_obj = App.get_or_none(App.app_id == app_id, App.user == user)
    if not app_obj:
        return jsonify({'error': 'アプリが見つかりません。'}), 404

    if request.method == 'DELETE':
        app_obj.delete_instance()
        assign_top_flag(user)
        flash('アプリを削除しました。', 'info')
        return jsonify({'success': True})

    payload = request.get_json(silent=True) or {}
    app_obj.app_type = payload.get('app_type', app_obj.app_type)
    app_obj.app_name = payload.get('app_name', app_obj.app_name)
    app_obj.app_day = payload.get('app_day', app_obj.app_day)
    app_time = payload.get('app_time', app_obj.app_time)
    try:
        app_obj.app_time = int(app_time)
    except (TypeError, ValueError):
        pass
    app_obj.app_top = bool(payload.get('app_top', app_obj.app_top))
    app_obj.save()
    assign_top_flag(user)
    flash('アプリ情報を更新しました。', 'info')
    return jsonify(_serialize_app(app_obj))


@app.route('/api/personal/stats')
def api_personal_stats():
    user = _current_user()
    if not user:
        return jsonify({'error': 'ログインが必要です。'}), 401
    apps = list(App.select().where(App.user == user))
    payload = build_stats_payload(apps)
    payload['top_app'] = top_app(user)
    return jsonify(payload)


@app.route('/api/global/stats')
def api_global_stats():
    apps = list(App.select())
    payload = build_stats_payload(apps)
    payload['top_app'] = top_app()
    return jsonify(payload)


def _render_stats_page(**context):
    return render_template('stats.html', **context)


@app.route('/stats/personal')
def stats_personal():
    user = _current_user()
    if not user:
        flash('ログインが必要です。', 'error')
        return redirect(url_for('index'))
    return _render_stats_page(
        title=f'{user.user_name}さんの集計',
        user=user,
        stats_endpoint=url_for('api_personal_stats'),
        personal_url=url_for('personal'),
        other_url=url_for('stats_global'),
        other_label='全体集計へ',
    )


@app.route('/stats/global')
def stats_global():
    return _render_stats_page(
        title='全体集計',
        user=None,
        stats_endpoint=url_for('api_global_stats'),
        personal_url=url_for('personal'),
        other_url=url_for('stats_personal'),
        other_label='個人集計へ',
    )


@app.route('/api/users', methods=['GET', 'POST'])
def api_users():
    if request.method == 'GET':
        users = User.select().order_by(User.user_name)
        return jsonify([
            {
                'user_id': u.user_id,
                'user_name': u.user_name,
            }
            for u in users
        ])

    payload = request.get_json(silent=True) or {}
    user_name = payload.get('user_name', '').strip()
    user_password = payload.get('user_password', '').strip()
    if not user_name or not user_password:
        return jsonify({'error': 'ユーザー名とパスワードは必須です。'}), 400
    user = User.create(user_name=user_name, user_password=user_password)
    flash('ユーザーを追加しました。', 'info')
    return jsonify({'user_id': user.user_id, 'user_name': user.user_name}), 201


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
