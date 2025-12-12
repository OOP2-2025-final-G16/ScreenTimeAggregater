from flask import Blueprint, render_template, request, redirect, url_for
from models import User

# Blueprintの作成
user_bp = Blueprint('user', __name__, url_prefix='/users')


@user_bp.route('/')
def list():
    users = User.select()
    return render_template('user_list.html', title='ユーザー一覧', items=users)


@user_bp.route('/add', methods=['GET', 'POST'])
def add():
    
    if request.method == 'POST':
        user_name = request.form['user_name']
        user_password = request.form['user_password']
        User.create(user_name=user_name, user_password=user_password)
        return redirect(url_for('user.list'))
    
    return render_template('user_add.html')

