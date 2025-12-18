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

# ------------------------------------------------------------------
# 共通ユーティリティ
# ------------------------------------------------------------------

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

def _get_user_apps(user):
    return (
        App.select()
        .where(App.user == user)
        .order_by(App.app_day.desc(), App.app_time.desc())
    )

# ------------------------------------------------------------------
# 画面遷移用ルート（HTMLを返す）
# ------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def index():
    """ログイン画面。POST時は認証を行いアプリ一覧(personal)へ遷移"""
    if request.method == 'POST':
        user_name = request.form.get('user_name', '').strip()
        user_password = request.form.get('user_password', '').strip()
        user = User.get_or_none(
            (User.user_name == user_name) & (User.user_password == user_password)
        )
        if user:
            session['user_id'] = user.user_id
            return redirect(url_for('personal'))  # ログイン後はアプリ一覧へ
        flash('ユーザー名またはパスワードが正しくありません。', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('ログアウトしました。', 'info')
    return redirect(url_for('index'))

@app.route('/personal')
def personal():
    """マイページ（アプリ管理画面）"""
    user = _current_user()
    if not user:
        flash('ログインが必要です。', 'error')
        return redirect(url_for('index'))
    apps = list(_get_user_apps(user))
    return render_template('personal_dashboard.html', user=user, apps=apps)

@app.route('/personal/apps/add', methods=['POST'])
def personal_add_app():
    """HTMLフォームからのアプリ追加（BuildError解消用）"""
    user = _current_user()
    if not user:
        return redirect(url_for('index'))

    app_name = request.form.get('app_name', '').strip() or '名称未設定'
    app_type = request.form.get('app_type', '').strip() or '未分類'
    try:
        app_time = int(request.form.get('app_time', 0))
    except (TypeError, ValueError):
        app_time = 0
    app_day = request.form.get('app_day', '').strip() or datetime.now().strftime('%Y-%m-%d')

    App.create(
        user=user,
        app_name=app_name,
        app_type=app_type,
        app_time=app_time,
        app_day=app_day,
        app_top=False,
    )
    assign_top_flag(user)
    flash('アプリ情報を登録しました。', 'info')
    return redirect(url_for('personal'))

@app.route('/personal/apps/<int:app_id>/delete', methods=['POST'])
def personal_delete_app(app_id):
    """HTMLフォームからのアプリ削除（BuildError解消用）"""
    user = _current_user()
    if not user:
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
def user_list():
    """ユーザー一覧"""
    users = list(User.select().order_by(User.user_name))
    return render_template('user_list.html', title='ユーザー一覧', items=users)

@app.route('/users/add', methods=['GET', 'POST'])
def users_add():
    """ユーザー追加"""
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
        return redirect(url_for('user_list'))
    return render_template('user_add.html')

@app.route('/stats/personal')
def stats_personal():
    """個人統計画面"""
    user = _current_user()
    if not user:
        return redirect(url_for('index'))
    return render_template(
        'index.html',
        title=f'{user.user_name}さんの集計',
        user=user,
        stats_endpoint=url_for('api_personal_stats'),
        personal_url=url_for('personal'),
        other_url=url_for('stats_global'),
        other_label='全体集計へ',
    )

@app.route('/')
def stats_global():
    """全体統計画面"""
    return render_template(
        'index.html',
        title='全体集計',
        user=None,
        stats_endpoint=url_for('api_global_stats'),
        personal_url=url_for('personal'),
        other_url=url_for('stats_personal'),
        other_label='個人集計へ',
    )

# ------------------------------------------------------------------
# APIルート（JSONを返す）
# ------------------------------------------------------------------

@app.route('/api/personal/apps', methods=['GET', 'POST'])
def api_personal_apps():
    user = _current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    if request.method == 'GET':
        apps = _get_user_apps(user)
        return jsonify([_serialize_app(app_obj) for app_obj in apps])
    
    # POST処理（JSからの追加）
    payload = request.get_json(silent=True) or {}
    app_obj = App.create(
        user=user,
        app_type=payload.get('app_type', '未分類'),
        app_name=payload.get('app_name', '名称未設定'),
        app_time=int(payload.get('app_time', 0)),
        app_day=payload.get('app_day') or datetime.now().strftime('%Y-%m-%d'),
        app_top=False,
    )
    assign_top_flag(user)
    return jsonify(_serialize_app(app_obj)), 201

@app.route('/api/personal/stats')
def api_personal_stats():
    user = _current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
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

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)