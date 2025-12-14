(() => {
    const configEl = document.getElementById('stats-config');
    if (!configEl) {
        return;
    }

    const endpoint = configEl.dataset.endpoint;
    if (!endpoint) {
        return;
    }

    const topAppInfo = document.getElementById('topAppInfo');
    const ratioLabel = document.getElementById('ratioTotalLabel');
    const typeLabel = document.getElementById('typeTotalLabel');
    const weeklyCanvas = document.getElementById('weeklyChart');
    const ratioCanvas = document.getElementById('ratioChart');
    const typeCanvas = document.getElementById('typeChart');

    let weeklyChart;
    let ratioChart;
    let typeChart;

    function renderCharts(payload) {
        if (!payload) {
            return;
        }

        if (topAppInfo) {
            if (payload.top_app) {
                const owner = payload.top_app.user_name ? `（${payload.top_app.user_name}さん）` : '';
                topAppInfo.textContent = `トップアプリ: ${payload.top_app.app_name} ${owner} / ${payload.top_app.app_time} 分 / ${payload.top_app.app_day}`;
            } else {
                topAppInfo.textContent = '対象データがありません。';
            }
        }

        const weekly = payload.weekly || { labels: [], data: [] };
        const ratio = payload.ratio || { labels: [], data: [], total: 0 };
        const typeData = payload.type || { labels: [], data: [], total: 0 };

        const createChart = (canvas, cfg) => {
            if (!canvas) {
                return null;
            }
            const context = canvas.getContext('2d');
            if (!context) {
                return null;
            }
            return new Chart(context, cfg);
        };

        if (weeklyCanvas) {
            weeklyChart?.destroy();
            weeklyChart = createChart(weeklyCanvas, {
                type: 'line',
                data: {
                    labels: weekly.labels,
                    datasets: [
                        {
                            label: '1日あたりの合計利用分',
                            data: weekly.data,
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59,130,246,.2)',
                            tension: 0.25,
                            fill: true,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: { display: true, text: '分' },
                        },
                    },
                },
            });
        }

        if (ratioCanvas) {
            ratioChart?.destroy();
            ratioChart = createChart(ratioCanvas, {
                type: 'doughnut',
                data: {
                    labels: ratio.labels,
                    datasets: [
                        {
                            label: 'アプリ別',
                            data: ratio.data,
                            backgroundColor: ['#ef4444', '#f97316', '#facc15', '#22c55e', '#0ea5e9', '#8b5cf6'],
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' },
                    },
                },
            });
            if (ratioLabel) {
                ratioLabel.textContent = `合計 ${ratio.total ?? 0} 分`;
            }
        }

        if (typeCanvas) {
            typeChart?.destroy();
            typeChart = createChart(typeCanvas, {
                type: 'doughnut',
                data: {
                    labels: typeData.labels,
                    datasets: [
                        {
                            label: '種別別',
                            data: typeData.data,
                            backgroundColor: ['#0ea5e9', '#14b8a6', '#22c55e', '#eab308', '#f97316', '#f43f5e'],
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' },
                    },
                },
            });
            if (typeLabel) {
                typeLabel.textContent = `合計 ${typeData.total ?? 0} 分`;
            }
        }
    }

    fetch(endpoint)
        .then((response) => {
            if (!response.ok) {
                throw new Error('統計データの取得に失敗しました。');
            }
            return response.json();
        })
        .then((payload) => {
            renderCharts(payload);
        })
        .catch((error) => {
            if (topAppInfo) {
                topAppInfo.textContent = error.message;
            }
            // eslint-disable-next-line no-console
            console.error(error);
        });
})();
