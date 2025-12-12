import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

# データベースファイル名 (カレントディレクトリにあることを前提)
DB_FILE = 'my_two_tables.db'

def get_db_data(table_name):
    """指定されたテーブル名から全てのデータを取得する関数"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  # カラム名でアクセスできるように設定
        cursor = conn.cursor()

        # SQLクエリを実行
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
        return {"columns": [], "rows": [], "error": f"データベースエラー ({table_name}): {e}"}
    
    finally:
        if conn:
            conn.close()

@app.route('/')
def index():
    """メインページにアクセスされたときの処理"""
    
    # データを取得するテーブル名
    tables_to_display = ['users', 'data_records']
    
    # 各テーブルのデータを取得
    all_table_data = {}
    for table_name in tables_to_display:
        all_table_data[table_name] = get_db_data(table_name)
    
    # テンプレートにデータを渡してレンダリング
    return render_template('debug_db_viewer.html', tables=all_table_data)

if __name__ == '__main__':
    # 開発サーバーを起動
    app.run(debug=True)