import sqlite3

# データベースファイル名
DB_FILE = 'my_two_tables.db'

def insert_sample_data():
    """
    既存のテーブルにサンプルデータを挿入します。
    """
    conn = None
    try:
        # 既存のデータベースファイルに接続
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # ----------------------------------------------------
        # 1. users テーブルへのデータ挿入
        # ----------------------------------------------------
        print("テーブル 'users' にデータを挿入します...")
        
        users_data = [
            ('alice_s', 'password123'),
            ('bob_t', 'securepwd'),
            ('charlie_u', 'mysecret')
        ]
        
        # INSERT ステートメント
        cursor.executemany("INSERT INTO users (name, password) VALUES (?, ?)", users_data)
        print(f"-> {cursor.rowcount} 件のユーザーデータを挿入しました。")


        # ----------------------------------------------------
        # 2. data_records テーブルへのデータ挿入
        # ----------------------------------------------------
        print("テーブル 'data_records' にデータを挿入します...")
        
        records_data = [
            (101, 'First record data'),
            (205, 'Important number'),
            (310, 'Another string value'),
            (50, None)  # strカラムはNULLも許可
        ]

        # INSERT ステートメント
        cursor.executemany("INSERT INTO data_records (number, str) VALUES (?, ?)", records_data)
        print(f"-> {cursor.rowcount} 件のレコードデータを挿入しました。")


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
        conn.row_factory = sqlite3.Row  # ヘッダー名でアクセス可能にする
        
        print("\n--- データ確認 ---")
        
        # usersテーブルのデータ確認
        print("\n[users テーブル]")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        for row in cursor.fetchall():
            print(dict(row))
            
        # data_recordsテーブルのデータ確認
        print("\n[data_records テーブル]")
        cursor.execute("SELECT * FROM data_records")
        for row in cursor.fetchall():
            print(dict(row))
            
    except sqlite3.Error as e:
        print(f"データ確認エラー: {e}")
    finally:
        if conn:
            conn.close()

# データ確認の実行
verify_data()