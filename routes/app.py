from flask import Blueprint, render_template, abort
from models import App, User


def _make_app_blueprint(name, url_prefix, title, order_field=None, filter_clause=None):
    bp = Blueprint(name, __name__, url_prefix=url_prefix)

    @bp.route('/')
    def list():
        query = App.select()
        if filter_clause is not None:
            query = query.where(filter_clause)
        if order_field is not None:
            query = query.order_by(order_field)
        return render_template('app_list.html', title=title, items=query)

    return bp


app_id_bp = _make_app_blueprint('app_id', '/apps/id', 'アプリID別', order_field=App.app_id)
app_type_bp = _make_app_blueprint('app_type', '/apps/type', 'アプリの種類別', order_field=App.app_type)
app_name_bp = _make_app_blueprint('app_name', '/apps/name', 'アプリの名前別', order_field=App.app_name)
app_time_bp = _make_app_blueprint('app_time', '/apps/time', '利用時間順', order_field=App.app_time.desc())
app_day_bp = _make_app_blueprint('app_day', '/apps/day', '利用日順', order_field=App.app_day)
app_top_bp = _make_app_blueprint(
    'app_top',
    '/apps/top',
    '最も利用されたアプリ',
    order_field=App.app_time.desc(),
    filter_clause=(App.app_top == True),
)


app_user_bp = Blueprint('app_user', __name__, url_prefix='/apps/user')


@app_user_bp.route('/')
def user_index():
    users = User.select().order_by(User.user_name)
    return render_template('app_user_list.html', title='ユーザー別アプリ', users=users)


@app_user_bp.route('/<int:user_id>')
def user_detail(user_id):
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        abort(404)
    apps = (
        App.select()
        .where(App.user == user)
        .order_by(App.app_time.desc(), App.app_name)
    )
    return render_template('app_list.html', title=f'{user.user_name} のアプリ', items=apps)