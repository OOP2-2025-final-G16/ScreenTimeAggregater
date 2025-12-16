(() => {
    const config = document.getElementById('apps-config');
    if (!config) {
        return;
    }
    const endpoint = config.dataset.endpoint;
    if (!endpoint) {
        return;
    }

    const tableBody = document.getElementById('appsBody');
    const emptyMessage = document.getElementById('appsEmpty');
    const form = document.getElementById('appCreateForm');
    const feedback = document.getElementById('appFormFeedback');
    const flashRoot = document.getElementById('appFlash');
    const refreshAppsBtn = document.getElementById('refresh-apps');
    const refreshStatsBtn = document.getElementById('refresh-stats');

    const showFlash = (message, type = 'info') => {
        if (!flashRoot) {
            return;
        }
        flashRoot.innerHTML = `<div class="flash ${type}">${message}</div>`;
        setTimeout(() => {
            flashRoot.innerHTML = '';
        }, 5000);
    };

    const renderApps = (apps) => {
        if (!tableBody) {
            return;
        }
        if (!apps.length) {
            tableBody.innerHTML = '<tr><td colspan="6">該当するアプリがありません。</td></tr>';
            emptyMessage?.removeAttribute('hidden');
            return;
        }
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
            await loadApps();
            window.dispatchEvent(new Event('personal-stats-refresh'));
        } catch (error) {
            console.error(error);
            showFlash(error.message, 'error');
        }
    };

    if (tableBody) {
        tableBody.addEventListener('click', (event) => {
            const button = event.target.closest('button[data-action="delete-app"]');
            if (!button) {
                return;
            }
            event.preventDefault();
            const appId = button.dataset.appId;
            if (!appId) {
                return;
            }
            if (confirm('アプリを削除してもよろしいですか？')) {
                deleteApp(appId);
            }
        });
    }

    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const data = new FormData(form);
            const payload = {
                app_type: data.get('app_type')?.toString().trim(),
                app_name: data.get('app_name')?.toString().trim(),
                app_time: Number(data.get('app_time')),
                app_day: data.get('app_day')?.toString(),
                app_top: data.get('app_top') === 'on',
            };
            const feedbackMessage = feedback;
            if (feedbackMessage) {
                feedbackMessage.textContent = '送信中...';
            }
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                });
                if (!response.ok) {
                    const errorPayload = await response.json().catch(() => ({}));
                    throw new Error(errorPayload.error || 'アプリの追加に失敗しました。');
                }
                form.reset();
                showFlash('アプリを追加しました。');
                await loadApps();
                window.dispatchEvent(new Event('personal-stats-refresh'));
            } catch (error) {
                console.error(error);
                if (feedbackMessage) {
                    feedbackMessage.textContent = '';
                }
                showFlash(error.message, 'error');
            } finally {
                if (feedbackMessage) {
                    feedbackMessage.textContent = '';
                }
            }
        });
    }

    refreshAppsBtn?.addEventListener('click', (event) => {
        event.preventDefault();
        loadApps();
    });

    refreshStatsBtn?.addEventListener('click', (event) => {
        event.preventDefault();
        window.dispatchEvent(new Event('personal-stats-refresh'));
    });

    loadApps();
})();