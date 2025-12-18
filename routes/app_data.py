from flask import Blueprint, render_template, request, redirect, url_for
# ユーザー、アプリ、使用データを管理するモデル（User, App, UsageDataなどを想定）
from models import App
from peewee import fn, SQL
from datetime import datetime

# Blueprintの作成: /usages というURLプレフィックスを設定
usage_bp = Blueprint('usage', __name__, url_prefix='/usages')


@usage_bp.route('/')
def list():
    # データベースからすべての使用データを取得
    usages = UsageData.select() 
    return render_template('usage_list.html', title='使用データ一覧', items=usages)


@usage_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # フォームからユーザーID、アプリ名、使用時間を取得
        user_id = request.form['user_id']
        app_name = request.form['app_name']
        app_type = request.form['app_type'] 
        
        # 使用時間は整数に変換 (フォームのname属性: app_time)
        try:
            app_time = int(request.form['app_time'])
        except ValueError:
            # エラー処理（例: 数値でない場合はフォームに戻るなど）
            return "エラー: 使用時間は数値で入力してください。", 400

        app_day_str = request.form['app_day'] # 日付文字列を取得 (YYYY-MM-DD形式)
        try:
            # 日付文字列を date 型に変換
            app_day = datetime.strptime(app_day_str, '%Y-%m-%d').date() 
        except ValueError:
            return "エラー: 使用日の形式が正しくありません。", 400
        
        # 新しい使用データをデータベースに作成
        UsageData.create(
            user_id=user_id, 
            app_name=app_name,
            app_type=app_type, 
            app_time=app_time,
            app_day=app_day
        )

        try:
            # 該当ユーザーの全使用データをジャンルごとに集計
            # Peeweeのaggregate関数を想定 (SUMやfn.SUM)
            type_totals = UsageData.select(
                UsageData.app_type, 
                fn.SUM(UsageData.app_time).alias('total_time')
            ).where(
                UsageData.user_id == user_id
            ).group_by(
                UsageData.app_type
            ).order_by(
                SQL('total_time').desc() # 合計時間の降順でソート
            ).limit(1) # 最上位のレコードのみ取得
            
            app_top_genre = None
            if type_totals:
                # 取得した結果からトップジャンル名を取得
                top_record = type_totals.get()
                app_top_genre = top_record.app_genre
                
            # 計算結果をUserモデルのapp_topフィールドに保存（Userモデルにapp_topが必要）
            # または、UsageDataに保存するならば...
            
            # ここではシンプルにUserモデルにトップジャンルを更新すると仮定します
            # Userモデルが定義されていることが前提
            user = App.get_or_none(App.user_id == user_id)
            if user:
                user.app_top = app_top_genre
                user.save()
                
        except Exception as e:
            # データベース接続やモデル操作のエラーをハンドル
            print(f"トップジャンル計算エラー: {e}")
            # エラーがあっても処理は継続させる
        
        # 一覧ページにリダイレクト
        return redirect(url_for('usage.list'))
    
    # GETリクエストの場合、データ入力フォームを表示
    # テンプレート名は 'usage_form.html' または 'usage_add.html' が適切
    return render_template('usage_add.html') # 先ほど作成したHTMLテンプレートに相当


@usage_bp.route('/edit/<int:usage_id>', methods=['GET', 'POST'])
def edit(usage_id):
    # 編集対象のデータ取得
    usage = UsageData.get_or_none(UsageData.id == usage_id)
    if not usage:
        return redirect(url_for('usage.list'))

    if request.method == 'POST':
        # フォームから更新データを取得
        usage.user_id = request.form['user_id']
        usage.app_name = request.form['app_name']
        
        try:
            usage.usage_time_minutes = int(request.form['usage_time_minutes'])
        except ValueError:
            return "エラー: 使用時間は数値で入力してください。", 400

        # データベースに保存
        usage.save()
        return redirect(url_for('usage.list'))

    # GETリクエストの場合、編集フォームを表示
    return render_template('usage_edit.html', usage=usage)