(() => {
    const configNode = document.getElementById('stats-config');
    if (!configNode) {
        return;
    }
    const endpoint = configNode.dataset.endpoint;
    if (!endpoint) {
        return;
    }

    const topAppNode = document.getElementById('topAppInfo');
    const weeklyCtx = document.getElementById('weeklyChart')?.getContext('2d');
    const ratioCtx = document.getElementById('ratioChart')?.getContext('2d');
    const typeCtx = document.getElementById('typeChart')?.getContext('2d');
    const ratioTotalLabel = document.getElementById('ratioTotalLabel');
    const typeTotalLabel = document.getElementById('typeTotalLabel');

    let weeklyChart;
    let ratioChart;
    let typeChart;

    const ratioColors = ['#1976d2', '#ffca28', '#66bb6a', '#ef5350', '#ab47bc', '#29b6f6'];
    const typeColors = ['#42a5f5', '#ffb300', '#9ccc65', '#f06292', '#29b6f6', '#7e57c2'];

    function renderWeeklyChart(labels, values) {
        if (!weeklyCtx) {
            return;
        }
        if (weeklyChart) {
            weeklyChart.destroy();
        }
        weeklyChart = new Chart(weeklyCtx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: '合計分数',
                        data: values,
                        borderColor: '#1976d2',
                        backgroundColor: 'rgba(25, 118, 210, 0.25)',
                        fill: true,
                        tension: 0.3,
                    },
                ],
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 30,
                        },
                    },
                },
            },
        });
    }

    function renderDoughnutChart(ctx, labels, values, colors) {
        if (!ctx) {
            return null;
        }
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [
                    {
                        data: values,
                        backgroundColor: colors,
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((acc, cur) => acc + cur, 0);
                                const percent = total ? ((value / total) * 100).toFixed(1) : '0.0';
                                return `${label}: ${value}分 (${percent}%)`;
                            },
                        },
                    },
                },
            },
        });
    }

    function updateTopApp(topApp) {
        if (!topApp || !topApp.name) {
            topAppNode.textContent = '登録されたアプリがまだありません。';
            return;
        }
        const name = topApp.name;
        const time = topApp.time ?? 0;
        topAppNode.innerHTML = `<strong>一番使われたアプリ:</strong> ${name} (${time} 分)`;
    }

    async function loadStats() {
        try {
            const response = await fetch(endpoint, { credentials: 'same-origin' });
            if (!response.ok) {
                throw new Error('集計データの取得に失敗しました。');
            }
            const data = await response.json();
            updateTopApp(data.top_app);
            if (ratioTotalLabel) {
                ratioTotalLabel.textContent = `合計: ${data.ratio_total ?? 0} 分`;
            }
            if (typeTotalLabel) {
                typeTotalLabel.textContent = `合計: ${data.type_total ?? 0} 分`;
            }
            renderWeeklyChart(data.weekly_labels || [], data.weekly_values || []);
            if (ratioChart) {
                ratioChart.destroy();
            }
            ratioChart = renderDoughnutChart(
                ratioCtx,
                data.ratio_labels || [],
                data.ratio_values || [],
                ratioColors,
            );
            if (typeChart) {
                typeChart.destroy();
            }
            typeChart = renderDoughnutChart(
                typeCtx,
                data.type_labels || [],
                data.type_values || [],
                typeColors,
            );
        } catch (error) {
            console.error(error);
            if (topAppNode) {
                topAppNode.textContent = '集計データの取得に失敗しました。';
            }
        }
    }

    loadStats();
    window.addEventListener('personal-stats-refresh', loadStats);
})();
