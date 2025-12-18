(() => {
    /**
     * 1. 初期設定とDOM要素（描画先）の取得
     */
    const configNode = document.getElementById('stats-config');
    if (!configNode) return;

    // APIの取得先URLをデータ属性から取得
    const endpoint = configNode.dataset.endpoint;
    if (!endpoint) return;

    // 情報を表示するテキスト要素と、グラフを描画するCanvasのコンテキストを取得
    const topAppNode = document.getElementById('topAppInfo');
    const weeklyCtx = document.getElementById('weeklyChart')?.getContext('2d'); // 週間推移（折れ線）
    const ratioCtx = document.getElementById('ratioChart')?.getContext('2d');   // アプリ別割合（ドーナツ）
    const typeCtx = document.getElementById('typeChart')?.getContext('2d');     // カテゴリ別割合（ドーナツ）
    
    // 合計時間を表示するラベル
    const ratioTotalLabel = document.getElementById('ratioTotalLabel');
    const typeTotalLabel = document.getElementById('typeTotalLabel');

    // Chartインスタンス保持用（更新時に古いグラフを破棄するために必要）
    let weeklyChart;
    let ratioChart;
    let typeChart;

    // グラフの色定義
    const ratioColors = ['#1976d2', '#ffca28', '#66bb6a', '#ef5350', '#ab47bc', '#29b6f6'];
    const typeColors = ['#42a5f5', '#ffb300', '#9ccc65', '#f06292', '#29b6f6', '#7e57c2'];

    /**
     * 2. 週間推移グラフ（折れ線グラフ）の描画
     */
    function renderWeeklyChart(labels, values) {
        if (!weeklyCtx) return;

        // 既存のグラフがある場合は、メモリリーク防止のため一度破棄する
        if (weeklyChart) {
            weeklyChart.destroy();
        }

        weeklyChart = new Chart(weeklyCtx, {
            type: 'line',
            data: {
                labels, // X軸のラベル（日付など）
                datasets: [{
                    label: '合計分数',
                    data: values, // Y軸の値
                    borderColor: '#1976d2',
                    backgroundColor: 'rgba(25, 118, 210, 0.25)',
                    fill: true,     // エリアを塗りつぶす
                    tension: 0.3,  // 線を少し滑らかにする
                }],
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 30 },
                    },
                },
            },
        });
    }

    /**
     * 3. 割合グラフ（ドーナツ型グラフ）の共通描画関数
     */
    function renderDoughnutChart(ctx, labels, values, colors) {
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                }],
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            // ホバー時に「ラベル: 分数 (パーセント)」を表示するカスタマイズ
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

    /**
     * 4. 最多使用アプリ情報の更新
     */
    function updateTopApp(topApp) {
        if (!topApp || !topApp.name) {
            topAppNode.textContent = '登録されたアプリがまだありません。';
            return;
        }
        const name = topApp.name;
        const time = topApp.time ?? 0;
        topAppNode.innerHTML = `<strong>一番使われたアプリ:</strong> ${name} (${time} 分)`;
    }

    /**
     * 5. データの取得と反映（メイン処理）
     */
    async function loadStats() {
        try {
            const response = await fetch(endpoint, { credentials: 'same-origin' });
            if (!response.ok) {
                throw new Error('集計データの取得に失敗しました。');
            }
            const data = await response.json();

            // テキスト情報の更新
            updateTopApp(data.top_app);
            if (ratioTotalLabel) ratioTotalLabel.textContent = `合計: ${data.ratio_total ?? 0} 分`;
            if (typeTotalLabel) typeTotalLabel.textContent = `合計: ${data.type_total ?? 0} 分`;

            // 折れ線グラフの描画
            renderWeeklyChart(data.weekly_labels || [], data.weekly_values || []);

            // ドーナツグラフ（アプリ別）の再描画
            if (ratioChart) ratioChart.destroy();
            ratioChart = renderDoughnutChart(
                ratioCtx,
                data.ratio_labels || [],
                data.ratio_values || [],
                ratioColors,
            );

            // ドーナツグラフ（カテゴリ別）の再描画
            if (typeChart) typeChart.destroy();
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

    // 初回実行
    loadStats();

    /**
     * 6. 外部（管理側スクリプトなど）からの更新イベントを受け取る
     * アプリを削除・追加した時に発行されるイベントをリッスンし、グラフを最新にする
     */
    window.addEventListener('personal-stats-refresh', loadStats);
})();