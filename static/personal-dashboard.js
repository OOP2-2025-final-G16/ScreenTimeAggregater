(() => {
    /**
     * 1. 初期設定とDOM要素の取得
     */
    const config = document.getElementById('apps-config');
    if (!config) return;

    const endpoint = config.dataset.endpoint;
    if (!endpoint) return;

    // UIパーツの参照
    const tableBody = document.getElementById('appsBody');      // 一覧表示先
    const emptyMessage = document.getElementById('appsEmpty');  // 空状態のメッセージ
    const form = document.getElementById('appCreateForm');      // 新規作成フォーム
    const feedback = document.getElementById('appFormFeedback');// 送信中などのフィードバック
    const flashRoot = document.getElementById('appFlash');      // 通知メッセージ表示エリア
    const refreshAppsBtn = document.getElementById('refresh-apps');
    const refreshStatsBtn = document.getElementById('refresh-stats');

    /**
     * 2. ユーティリティ関数
     */

    // 通知メッセージ（フラッシュ）を表示する
    const showFlash = (message, type = 'info') => {
        if (!flashRoot) return;
        flashRoot.innerHTML = `<div class="flash ${type}">${message}</div>`;
        setTimeout(() => {
            flashRoot.innerHTML = ''; // 5秒後に消去
        }, 5000);
    };

    /**
     * 3. データ取得・レンダリング処理
     */

    // アプリ一覧をテーブルに描画する
    const renderApps = (apps) => {
        if (!tableBody) return;

        // データが空の場合の処理
        if (!apps.length) {
            tableBody.innerHTML = '<tr><td colspan="6">該当するアプリがありません。</td></tr>';
            emptyMessage?.removeAttribute('hidden');
            return;
        }

        // データをループしてHTMLを生成
        emptyMessage?.setAttribute('hidden', '');
        tableBody.innerHTML = apps
            .map((app) => {
                const topLabel = app.app_top ? '⭐' : '—';
                return `
                    <tr>
                        <td>${app.app_type || '未分類'}</td>
                        <td>${app.app_name || '名称未設定'}</td>
                        <td>${app.app_time ?? 0}</td>
                        <td>${app.app_day || '-'}</td>
                        <td>${topLabel}</td>
                        <td>
                            <button class="link-button danger" data-action="delete-app" data-app-id="${app.app_id}">削除</button>
                        </td>
                    </tr>
                `;
            })
            .join('');
    };

    // サーバーからアプリ一覧を取得する
    const loadApps = async () => {
        try {
            const response = await fetch(endpoint, { credentials: 'same-origin' });
            if (!response.ok) {
                throw new Error('アプリ一覧の取得に失敗しました。');
            }
            const apps = await response.json();
            renderApps(apps);
        } catch (error) {
            console.error(error);
            tableBody.innerHTML = '<tr><td colspan="6">アプリの取得に失敗しました。</td></tr>';
            showFlash('アプリ一覧の取得に失敗しました。', 'error');
        }
    };

    /**
     * 4. 削除・登録処理
     */

    // 特定のアプリを削除する
    const deleteApp = async (appId) => {
        const url = `${endpoint}/${appId}`;
        try {
            const response = await fetch(url, {
                method: 'DELETE',
                credentials: 'same-origin',
            });
            if (!response.ok) {
                const errorPayload = await response.json().catch(() => ({}));
                throw new Error(errorPayload.error || 'アプリの削除に失敗しました。');
            }
            showFlash('アプリを削除しました。');
            await loadApps(); // 一覧を再読み込み
            // 他のコンポーネント（統計など）に更新を通知
            window.dispatchEvent(new Event('personal-stats-refresh'));
        } catch (error) {
            console.error(error);
            showFlash(error.message, 'error');
        }
    };

    /**
     * 5. イベントリスナーの設定
     */

    // 一覧内の「削除」ボタンクリック（イベント委譲を利用）
    if (tableBody) {
        tableBody.addEventListener('click', (event) => {
            const button = event.target.closest('button[data-action="delete-app"]');
            if (!button) return;

            event.preventDefault();
            const appId = button.dataset.appId;
            if (!appId) return;

            if (confirm('アプリを削除してもよろしいですか？')) {
                deleteApp(appId);
            }
        });
    }

    // 新規登録フォームの送信
    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            // フォームデータの構築
            const data = new FormData(form);
            const payload = {
                app_type: data.get('app_type')?.toString().trim(),
                app_name: data.get('app_name')?.toString().trim(),
                app_time: Number(data.get('app_time')),
                app_day: data.get('app_day')?.toString(),
                app_top: data.get('app_top') === 'on',
            };

            if (feedback) feedback.textContent = '送信中...';

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });

                if (!response.ok) {
                    const errorPayload = await response.json().catch(() => ({}));
                    throw new Error(errorPayload.error || 'アプリの追加に失敗しました。');
                }

                form.reset(); // フォームをクリア
                showFlash('アプリを追加しました。');
                await loadApps(); // 一覧を更新
                window.dispatchEvent(new Event('personal-stats-refresh'));
            } catch (error) {
                console.error(error);
                showFlash(error.message, 'error');
            } finally {
                if (feedback) feedback.textContent = '';
            }
        });
    }

    // アプリ一覧の更新ボタン
    refreshAppsBtn?.addEventListener('click', (event) => {
        event.preventDefault();
        loadApps();
    });

    // 統計情報の更新ボタン
    refreshStatsBtn?.addEventListener('click', (event) => {
        event.preventDefault();
        window.dispatchEvent(new Event('personal-stats-refresh'));
    });

    // 初回実行：アプリ一覧を読み込む
    loadApps();
})();