import sqlite3
import os

# データベースファイル名
DB_FILE = 'my_two_tables.db'

def create_database_and_tables():
    """
    データベースファイルを作成し、2つのテーブルを定義します。
    """
    # カレントディレクトリにデータベースファイルを作成し、接続
    # ファイルが存在しない場合は新規作成されます
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # ----------------------------------------------------
        # 1. テーブル名: users (ID, name, password)
        # ----------------------------------------------------
        print("テーブル 'users' を作成します...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        ''')

        # ----------------------------------------------------
        # 2. テーブル名: data_records (ID, number, str)
        # ----------------------------------------------------
        print("テーブル 'data_records' を作成します...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER NOT NULL,
                str TEXT
            );
        ''')
        
        # 変更をデータベースにコミット（保存）
        conn.commit()
        print(f"\n✅ データベース '{DB_FILE}' がカレントディレクトリに作成されました。")
        
        # 作成されたテーブルの確認
        print("\n--- 作成されたテーブル一覧 ---")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"- {table[0]}")
            
    except sqlite3.Error as e:
        print(f"データベースエラーが発生しました: {e}")
        
    finally:
        # 接続を閉じる
        if conn:
            conn.close()

# スクリプトの実行
create_database_and_tables()

# 実行後のファイルパス確認
print(f"\nデータベースファイルのパス: {os.path.join(os.getcwd(), DB_FILE)}")