import sqlite3
import os

# データベースファイル名
DB_FILE = 'my_app_data.db'

def create_initial_tables():
    """
    データベースファイルを作成し、ご指定の2つのテーブルを定義します。
    screen_time_data_tableの主キーを user_id に変更し、app_id カラムは削除されます。
    """
    conn = None
    try:
        # データベースファイルに接続 (ファイルがなければ作成されます)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # ----------------------------------------------------
        # 1. テーブル名: login_table (変更なし)
        # ----------------------------------------------------
        print("テーブル 'login_table' を作成します...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_table (
                user_name TEXT NOT NULL UNIQUE,
                user_id INTEGER PRIMARY KEY,      -- ユーザーID (数字、主キー)
                user_password TEXT NOT NULL
            );
        ''')

        # ----------------------------------------------------
        # 2. テーブル名: screen_time_data_table (修正済み)
        # ----------------------------------------------------
        print("テーブル 'screen_time_data_table' を作成します...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screen_time_data_table (
                user_id INTEGER PRIMARY KEY,           -- ユーザーID (数字、新しい主キー)
                app_type INTEGER,                      -- アプリの種別 (数字)
                app_name TEXT NOT NULL,                -- アプリ名 (文字列、必須)
                app_time REAL NOT NULL,                -- 利用時間 (REAL型)
                app_day INTEGER NOT NULL,              -- 利用日 (数字/日付をYYYYMMDD形式などで保持)
                app_top INTEGER                        -- 起動回数や優先度などの指標 (数字)
            );
        ''')
        
        # 変更をデータベースにコミット（保存）
        conn.commit()
        print(f"\n✅ データベース '{DB_FILE}' がカレントディレクトリに作成されました。")
        
    except sqlite3.Error as e:
        print(f"データベースエラーが発生しました: {e}")
        
    finally:
        # 接続を閉じる
        if conn:
            conn.close()

# スクリプトの実行
create_initial_tables()

# 実行後のファイルパス確認
print(f"\nデータベースファイルのパス: {os.path.join(os.getcwd(), DB_FILE)}")