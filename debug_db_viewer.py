import sqlite3
from flask import Flask, render_template

# Flaskアプリケーションのインスタンス化
app = Flask(__name__)

# データベースファイル名
# 新しいファイル名 (my_app_data.db) を使用
DB_FILE = 'my_app_data.db'

def get_db_data(table_name):
    """
    指定されたテーブル名から全てのデータを取得する関数。
    データは辞書のリストとして返されます。
    """
    conn = None
    try:
        # データベースに接続
        conn = sqlite3.connect(DB_FILE)
        # 取得したデータをカラム名でアクセスできるように設定
        conn.row_factory = sqlite3.Row  
        cursor = conn.cursor()

        # SQLクエリを実行
        # テーブル名が外部からの入力であるため、f-stringを使っていますが、
        # 通常はSQLインジェクション防止のため、テーブル名もホワイトリストでチェックすべきです。
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if rows:
            # カラム名（ヘッダー）をキーから取得
            columns = rows[0].keys()
            # 行データを辞書のリストとして取得
            data = [dict(row) for row in rows]
            return {"columns": columns, "rows": data, "error": None}
        else:
            return {"columns": [], "rows": [], "error": "データがありません。"}

    except sqlite3.Error as e:
        # データベース接続またはクエリ実行エラーが発生した場合
        return {"columns": [], "rows": [], "error": f"データベースエラー ({table_name}): {e}"}
    
    finally:
        # 接続を閉じる
        if conn:
            conn.close()

@app.route('/')
def index():
    """メインページ (http://127.0.0.1:5000/) にアクセスされたときの処理"""
    
    # 【重要】データを取得する新しいテーブル名を設定
    tables_to_display = ['login_table', 'screen_time_data_table']
    
    # 各テーブルのデータを取得
    all_table_data = {}
    for table_name in tables_to_display:
        # 取得したデータを辞書に格納 (キーはテーブル名)
        all_table_data[table_name] = get_db_data(table_name)
    
    # テンプレートにデータを渡してレンダリング
    return render_template('debug_db_viewer.html', tables=all_table_data)

if __name__ == '__main__':
    # 開発サーバーを起動
    # debug=True に設定すると、コード変更時に自動で再起動します
    app.run(debug=True)