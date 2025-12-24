(() => {
    const scriptEl = document.currentScript || document.querySelector('script[data-auto-logout]');
    const dataset = scriptEl?.dataset ?? {};
    const DEFAULT_TIMEOUT_MS = 15 * 60 * 1000; // 15 minutes
    const DEFAULT_HEARTBEAT_INTERVAL_MS = 2 * 60 * 1000; // 2 minutes
    const requestedTimeout = dataset.timeout !== undefined ? Number(dataset.timeout) : DEFAULT_TIMEOUT_MS;
    const inactivityTimeout = Number.isFinite(requestedTimeout) ? requestedTimeout : DEFAULT_TIMEOUT_MS;
    const logoutUrl = dataset.logoutUrl || '/logout';
    // 設定がなければデフォルトのログアウト・リダイレクト先を使う。
    const redirectUrl = dataset.redirectUrl || '/login';
    const heartbeatUrl = dataset.heartbeatUrl || '/heartbeat';
    const heartbeatInterval = Number(dataset.heartbeatInterval) || DEFAULT_HEARTBEAT_INTERVAL_MS;

    let timerId;
    let hasLoggedOut = false;
    let heartbeatId;
    let navigationIntent = false;

    const triggerLogout = () => {
        if (hasLoggedOut) {
            return;
        }
        hasLoggedOut = true;
        clearTimeout(timerId);
        fetch(logoutUrl, {
            method: 'GET',
            credentials: 'same-origin',
            keepalive: true,
        })
            .catch(() => {})
            .finally(() => {
                // サーバー側のセッション切断後、ログイン画面へリダイレクトする。
                window.location.href = redirectUrl;
            });
        cleanupHeartbeat();
    };

    const timerEnabled = inactivityTimeout > 0;
    // タイマーが有効なときだけユーザー操作を監視する。
    const scheduleLogout = () => {
        if (!timerEnabled || hasLoggedOut) {
            return;
        }
        clearTimeout(timerId);
        timerId = window.setTimeout(triggerLogout, inactivityTimeout);
        // inactivityTimeoutが経過した後にログアウトをトリガーする。
    };

    const updateActivity = () => {
        if (!timerEnabled) {
            return;
        }
        scheduleLogout();
    };
    // 操作を検知するたびにログアウトタイマーをリセットする。

    const activityEvents = ['click', 'keydown', 'mousemove', 'scroll', 'touchstart'];
    if (timerEnabled) {
        activityEvents.forEach((eventName) => {
            window.addEventListener(eventName, updateActivity, { passive: true });
        });
    }
    // クリックやキー入力などをトラッキングして再ログアウトまでの時間をリセットする。

    const markNavigationIntent = () => {
        navigationIntent = true;
        window.setTimeout(() => {
            navigationIntent = false;
        }, 1000);
    };
    // ユーザーがリンクを踏んだ・送信した直後は自動ログアウトの妨げとするフラグを立てる。

    document.addEventListener('click', (event) => {
        const anchor = event.target.closest('a[href]');
        if (!anchor) {
            return;
        }
        if (anchor.target === '_blank') {
            return;
        }
        markNavigationIntent();
    });
    // リンククリック／フォーム送信は自然な遷移とみなして強制ログアウトを抑制。

    document.addEventListener('submit', () => {
        markNavigationIntent();
    });

    window.addEventListener('beforeunload', () => {
        if (navigationIntent || hasLoggedOut) {
            return;
        }
        fetch(logoutUrl, {
            method: 'GET',
            credentials: 'same-origin',
            keepalive: true,
        }).catch(() => {});
    });
    // ページを離脱する際もログアウト API を叩いてセッションを確実に切る。

    const sendHeartbeat = () => {
        if (!heartbeatUrl) {
            return;
        }
        // サーバー側のセッション状態を維持するため、一定間隔で heartbeat を送信。
        fetch(heartbeatUrl, {
            method: 'POST',
            credentials: 'same-origin',
            keepalive: true,
        }).catch(() => {});
    };

    const startHeartbeat = () => {
        if (heartbeatId) {
            return;
        }
        sendHeartbeat();
        heartbeatId = window.setInterval(sendHeartbeat, heartbeatInterval);
        // heartbeatを定期的に送信するためのインターバルを設定する。
    };

    const cleanupHeartbeat = () => {
        if (!heartbeatId) {
            return;
        }
        window.clearInterval(heartbeatId);
        heartbeatId = undefined;
        // ループを解除して不要なリクエストを止める。
    };

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            scheduleLogout();
        }
    });
    // ページが可視状態に戻ったときにログアウトタイマーを再開する。

    startHeartbeat();
    if (timerEnabled) {
        scheduleLogout();
    }
})();
