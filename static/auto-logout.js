(() => {
    const scriptEl = document.currentScript || document.querySelector('script[data-auto-logout]');
    const dataset = scriptEl?.dataset ?? {};
    const DEFAULT_TIMEOUT_MS = 15 * 60 * 1000; // 15 minutes
    const DEFAULT_HEARTBEAT_INTERVAL_MS = 2 * 60 * 1000; // 2 minutes
    const requestedTimeout = dataset.timeout !== undefined ? Number(dataset.timeout) : DEFAULT_TIMEOUT_MS;
    const inactivityTimeout = Number.isFinite(requestedTimeout) ? requestedTimeout : DEFAULT_TIMEOUT_MS;
    const logoutUrl = dataset.logoutUrl || '/logout';
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
                window.location.href = redirectUrl;
            });
        cleanupHeartbeat();
    };

    const timerEnabled = inactivityTimeout > 0;
    const scheduleLogout = () => {
        if (!timerEnabled || hasLoggedOut) {
            return;
        }
        clearTimeout(timerId);
        timerId = window.setTimeout(triggerLogout, inactivityTimeout);
    };

    const updateActivity = () => {
        if (!timerEnabled) {
            return;
        }
        scheduleLogout();
    };

    const activityEvents = ['click', 'keydown', 'mousemove', 'scroll', 'touchstart'];
    if (timerEnabled) {
        activityEvents.forEach((eventName) => {
            window.addEventListener(eventName, updateActivity, { passive: true });
        });
    }

    const markNavigationIntent = () => {
        navigationIntent = true;
        window.setTimeout(() => {
            navigationIntent = false;
        }, 1000);
    };

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

    const sendHeartbeat = () => {
        if (!heartbeatUrl) {
            return;
        }
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
    };

    const cleanupHeartbeat = () => {
        if (!heartbeatId) {
            return;
        }
        window.clearInterval(heartbeatId);
        heartbeatId = undefined;
    };

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            scheduleLogout();
        }
    });

    startHeartbeat();
    if (timerEnabled) {
        scheduleLogout();
    }
})();
