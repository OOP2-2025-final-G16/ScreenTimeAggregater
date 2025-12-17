from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from models import initialize_database
from models.user import User

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # セッション管理用の秘密鍵

# データベースの初期化
initialize_database()

# ログインページ
@app.route('/')
def index():
    return render_template('login.html')

# ログイン処理
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user_name = data.get('user_name')
        user_password = data.get('user_password')
        
        # ユーザー認証
        user = User.get_or_none(User.user_name == user_name, User.user_password == user_password)
        
        if user:
            session['user_id'] = user.user_id
            session['user_name'] = user.user_name
            return jsonify({'success': True, 'message': 'ログインに成功しました'})
        else:
            return jsonify({'success': False, 'message': 'ユーザー名またはパスワードが間違っています'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': f'エラーが発生しました: {str(e)}'}), 500

# 新規ユーザー登録ページ
@app.route('/users/add')
def users_add():
    return render_template('user_add.html')

# 新規ユーザー登録処理
@app.route('/users/add', methods=['POST'])
def users_add_post():
    try:
        data = request.get_json()
        user_name = data.get('user_name')
        user_password = data.get('user_password')
        
        # ユーザー名の重複チェック
        if User.get_or_none(User.user_name == user_name):
            return jsonify({'success': False, 'message': 'このユーザー名は既に使用されています'}), 400
        
        # 新規ユーザー作成
        User.create(user_name=user_name, user_password=user_password)
        return jsonify({'success': True, 'message': 'ユーザー登録が完了しました'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'エラーが発生しました: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
