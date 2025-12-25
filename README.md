# アプリ名: ScreenTimeAggregater

OOP2Group16最終課題 スマホスクリーン集計アプリ

　ユーザーがアプリの利用時間を記録し、Chart.js を使ったダッシュボードで可視化する SPA 風のフロントエンドと、Flask + Peewee 構成バックエンドのデータ集計アプリです。
　機能概要としては、個別アプリの追加/削除、週次の合計時間とアプリ別・カテゴリ別割合の可視化、トップアプリのハイライト、そして非操作時に heartbeat/auto-logout を使ってセキュアにセッションを切る仕組みを含む統合的な統計ビューを提供します。
　集計処理を組み合わせ、`stats.html` では折れ線グラフとドーナツグラフ、トップアプリ表示一週間での使用時間が見ることができます。

## アピールポイント

- Flask + Peewee による SQLite ベースのデータ管理（`User`, `App` モデル）
- `personal-dashboard.html` から `/api/personal/apps` 経由でアプリデータを CRUD し、`personal-stats-refresh` イベントで `stats-charts.js` にリアルタイム更新を知らせる仕組み
- `stats-charts.js` は `weekly_*`, `ratio_*`, `type_*`, `top_app`, `*_total` のpayloadを Chart.js で再レンダーし、`logoutOnDisconnect()` + offline 対応でセッション状態を整える
- `auto-logout.js` は `data-timeout`/`heartbeat` 付きタイマーと `keepalive` を使って、非操作時の自動ログアウトとログアウト通知の信頼性を確保
- フロントページにログイン・アプリ追加・統計・自動ログアウトが共存する「統合ダッシュボード」体験を提供
- 左サイドに各ページへのボタンを置くことで遷移の操作が直感的になっている

## 動作条件

```bash
python 3.13 以上

# Python モジュール
Flask==3.0.3
peewee==3.17.7
```

## 起動手順

```bash
$ python app.py
# http://localhost:8080 にアクセス
```

## 画面構成のポイント

- `/personal` : ユーザーが `App` モデルにデータを登録・削除する CRUD フォーム
- `/stats/global` : `stats-charts.js` で `weeklyChart`, `ratioChart`, `typeChart` を描画し、`stats-config` に設定した `data-endpoint` から JSON を取得
- `/heartbeat`, `/logout` : `auto-logout.js` が `keepalive` 付きで polling/POST を送ることでセッション継続とクリーンアップを両立
- `static/personal-dashboard.js` : `window.dispatchEvent(new Event('personal-stats-refresh'))` で stats 側に更新通知

## 参考情報
- `models/__init__.py` で `SQLiteDatabase('my_database.db')` を初期化し、`App` / `User` モデルを登録
- `services/statistics.py` の `build_stats_payload`, `weekly_usage`, `top_app`, `type_ratio` などが Charts に渡すデータの供給元
- `static/stats-charts.js` は `logoutOnDisconnect()` を `fetch('/logout', { keepalive: true })` で呼び出し、再描画前に旧チャートを `destroy()` してメモリリーク防止
- `static/auto-logout.js` は `data-timeout` を 0 にするとタイマー機能を無効化し、`beforeunload`/`navigationIntent` で誤作動を防ぐ設計