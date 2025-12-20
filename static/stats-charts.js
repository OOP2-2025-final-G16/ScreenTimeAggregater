(() => {
    const configEl = document.getElementById('stats-config');
    if (!configEl) return;

    const endpoint = configEl.dataset.endpoint;
    if (!endpoint) return;

    const topAppEl = document.getElementById('topAppInfo');
    const weeklyCanvas = document.getElementById('weeklyChart');
    const ratioCanvas = document.getElementById('ratioChart');
    const typeCanvas = document.getElementById('typeChart');
    const ratioTotalLabel = document.getElementById('ratioTotalLabel');
    const typeTotalLabel = document.getElementById('typeTotalLabel');

    if (!weeklyCanvas || !ratioCanvas || !typeCanvas) {
        return;
    }

    const colorPalette = ['#0f62fe', '#198038', '#da1e28', '#ffc107', '#9c27b0', '#006d75', '#f78da7'];

    const createPalette = (count) => (
        Array.from({ length: count }, (_, index) => colorPalette[index % colorPalette.length])
    );

    let weeklyChart = null;
    let ratioChart = null;
    let typeChart = null;

    const ensureChartInstance = (chart, canvas, config) => {
        if (chart) {
            chart.options = config.options;
            chart.data = config.data;
            chart.update();
            return chart;
        }
        return new Chart(canvas.getContext('2d'), config);
    };

    const parseNumber = (value) => (typeof value === 'number' ? value : 0);

    const describeTopApp = (topApp) => {
        if (!topApp) {
            return 'まだアプリが登録されていません。';
        }
        const minutes = parseNumber(topApp.app_time);
        return `${topApp.app_name}（${topApp.app_type}）：${minutes.toLocaleString()} 分`;
    };

    const normalizeBuckets = (items) => {
        if (!items || !items.length) {
            return [{ label: 'データなし', total: 1, placeholder: true }];
        }
        return items;
    };

    const buildWeeklyConfig = (dataPoints) => {
        const labels = dataPoints.map((item) => item.label);
        const values = dataPoints.map((item) => parseNumber(item.total));
        return {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: '1日あたりの利用時間（分）',
                        data: values,
                        backgroundColor: '#0f62fecc',
                        borderColor: '#0f62fe',
                        borderRadius: 6,
                        borderWidth: 1,
                        barThickness: 22,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 30,
                        },
                    },
                },
            },
        };
    };

    const buildDonutConfig = (items) => {
        const normalized = normalizeBuckets(items);
        const labels = normalized.map((item) => item.label);
        const values = normalized.map((item) => parseNumber(item.total));
        const palette = createPalette(normalized.length);
        const colors = normalized.map((item, index) =>
            item.placeholder ? '#d3dce6' : palette[index]
        );
        return {
            type: 'doughnut',
            data: {
                labels,
                datasets: [
                    {
                        data: values,
                        backgroundColor: colors,
                        borderWidth: 0,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                        },
                    },
                },
            },
        };
    };

    const renderTotals = (value, element) => {
        if (!element) return;
        const minutes = parseNumber(value);
        element.textContent = `合計 ${minutes.toLocaleString()} 分`;
    };

    const renderPayload = (payload) => {
        if (topAppEl) {
            topAppEl.textContent = describeTopApp(payload.top_app);
        }

        const weeklyConfig = buildWeeklyConfig(payload.weekly || []);
        weeklyChart = ensureChartInstance(weeklyChart, weeklyCanvas, weeklyConfig);

        ratioChart = ensureChartInstance(ratioChart, ratioCanvas, buildDonutConfig(payload.app_ratios || []));
        typeChart = ensureChartInstance(typeChart, typeCanvas, buildDonutConfig(payload.type_ratios || []));

        renderTotals(payload.total_usage, ratioTotalLabel);
        renderTotals(payload.total_usage, typeTotalLabel);
    };

    const fetchAndRender = async () => {
        try {
            const response = await fetch(endpoint, { credentials: 'same-origin' });
            if (!response.ok) {
                throw new Error('集計データの取得に失敗しました。');
            }
            const payload = await response.json();
            renderPayload(payload);
        } catch (err) {
            if (topAppEl) {
                topAppEl.textContent = '集計データを取得できませんでした。';
            }
            console.error(err);
            // If charts exist, clear them to avoid stale data
            [weeklyChart, ratioChart, typeChart].forEach((chart) => chart?.destroy());
            weeklyChart = null;
            ratioChart = null;
            typeChart = null;
        }
    };

    fetchAndRender();
    window.addEventListener('personal-stats-refresh', fetchAndRender);
})();