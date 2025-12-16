import sqlite3

# データベースファイル名
DB_FILE = 'my_app_data.db' 

def insert_sample_data():
    """
    新しいテーブル定義に合うようにサンプルデータを挿入します。
    両テーブルの user_id の値を一致させます。
    """
    conn = None
    try:
        # 既存のデータベースファイルに接続
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # ----------------------------------------------------
        # 1. login_table へのデータ挿入 (データは前回のものを維持)
        # ----------------------------------------------------
        print("テーブル 'login_table' にデータを挿入します...")
        
        login_data = [
            # (user_name, user_id, user_password)
            ('alice_smith', 101, 'secure_pass_A'),
            ('bob_tanaka', 102, 'bob_secret_B'),
            ('charlie_dev', 103, 'dev_pwd_C')
        ]
        
        cursor.executemany("INSERT INTO login_table (user_name, user_id, user_password) VALUES (?, ?, ?)", login_data)
        print(f"-> {cursor.rowcount} 件のログインデータを挿入しました。")


        # ----------------------------------------------------
        # 2. screen_time_data_table へのデータ挿入 (user_idに変更)
        # ----------------------------------------------------
        print("テーブル 'screen_time_data_table' にデータを挿入します...")
        
        # user_id が PRIMARY KEY となり、login_table の user_id と同じ値を持つ
        screen_data = [
            # (user_id, app_type, app_name, app_time, app_day, app_top)
            # user_id 101, 102, 103 は login_table のユーザーに対応
            (101, 10, 'Youtube', 3600.5, 20251212, 5),
            (102, 20, 'Twitter', 1200.0, 20251212, 12),
            (103, 10, 'Game_A', 720.25, 20251211, 3),
            (104, 20, 'Twitter_2', 500.0, 20251211, 8),
            (105, 30, 'Browser', 180.0, 20251212, 4)
        ]

        # INSERT ステートメント: app_id が user_id に変更されました
        sql_insert_screen = """
        INSERT INTO screen_time_data_table 
            (user_id, app_type, app_name, app_time, app_day, app_top) 
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.executemany(sql_insert_screen, screen_data)
        print(f"-> {cursor.rowcount} 件のスクリーンタイムデータを挿入しました。")


        # 変更をデータベースにコミット（保存）
        conn.commit()
        print("\n✅ 全てのデータ挿入が完了しました。")

    except sqlite3.Error as e:
        print(f"データベースエラーが発生しました: {e}")
        
    finally:
        # 接続を閉じる
        if conn:
            conn.close()

# データの挿入を実行
insert_sample_data()

# ----------------------------------------------------
# 挿入されたデータを確認するための関数（オプション）
# ----------------------------------------------------
def verify_data():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        
        print("\n--- データ確認 ---")
        
        # login_tableのデータ確認
        print("\n[login_table]")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, user_name FROM login_table")
        for row in cursor.fetchall():
            print(dict(row))
            
        # screen_time_data_tableのデータ確認
        print("\n[screen_time_data_table] (user_idがPRIMARY KEY)")
        cursor.execute("SELECT user_id, app_name FROM screen_time_data_table")
        for row in cursor.fetchall():
            print(dict(row))
            
    except sqlite3.Error as e:
        print(f"データ確認エラー: {e}")
    finally:
        if conn:
            conn.close()

# データ確認の実行
verify_data()