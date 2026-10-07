document.addEventListener('DOMContentLoaded', () => {
    // Prevent multiple initializations
    if (window._dashboardInitialized) return;
    window._dashboardInitialized = true;

    // Fetch dashboard stats from API
    fetch('/api/dashboard-stats')
        .then(res => res.json())
        .then(data => {
            // Populate Stat Cards
            const avgScoreEl = document.getElementById('stats-ats-score');
            const resumesCountEl = document.getElementById('stats-resumes');
            const jobsCountEl = document.getElementById('stats-jobs');
            const avgMatchEl = document.getElementById('stats-avg-match');

            if (avgScoreEl) avgScoreEl.textContent = data.average_score !== undefined ? data.average_score : '--';
            if (resumesCountEl) resumesCountEl.textContent = data.resumes_count !== undefined ? data.resumes_count : '0';
            if (jobsCountEl) jobsCountEl.textContent = data.job_descriptions_count !== undefined ? data.job_descriptions_count : '0';
            if (avgMatchEl) avgMatchEl.textContent = data.average_score !== undefined ? `${data.average_score}%` : '--%';
            
            // Score distribution doughnut chart
            const scoreCanvas = document.getElementById('atsDistributionChart');
            if (scoreCanvas && data.score_distribution) {
                // Destroy existing chart instance if any to prevent memory leaks/glitches
                if (window._distChartInstance) {
                    window._distChartInstance.destroy();
                }
                const dist = data.score_distribution;
                const total = (dist.excellent || 0) + (dist.good || 0) + (dist.fair || 0) + (dist.poor || 0);

                window._distChartInstance = new Chart(scoreCanvas, {
                    type: 'doughnut',
                    data: {
                        labels: ['Excellent (90-100)', 'Good (75-89)', 'Fair (60-74)', 'Poor (0-59)'],
                        datasets: [{
                            data: total > 0 
                                ? [dist.excellent || 0, dist.good || 0, dist.fair || 0, dist.poor || 0]
                                : [0, 0, 0, 1], // Neutral state if no records
                            backgroundColor: total > 0
                                ? ['#C8FF3D', '#06b6d4', '#f59e0b', '#ef4444']
                                : ['#222623', '#222623', '#222623', '#222623'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        resizeDelay: 250,
                        animation: {
                            duration: 500
                        },
                        cutout: '72%',
                        plugins: {
                            legend: { 
                                position: 'bottom',
                                labels: {
                                    color: '#A8ADA5',
                                    font: { family: 'Inter', size: 11 },
                                    boxWidth: 12,
                                    padding: 14
                                }
                            }
                        }
                    }
                });
            }

            // Recent analyses bar chart
            const recentCanvas = document.getElementById('recentScoresChart');
            if (recentCanvas) {
                if (window._recentChartInstance) {
                    window._recentChartInstance.destroy();
                }

                const recentAnalyses = data.recent_analyses || [];
                const labels = recentAnalyses.length > 0 
                    ? recentAnalyses.map((a, i) => a.date || `Analysis #${i+1}`)
                    : ['No Analyses Yet'];
                const scores = recentAnalyses.length > 0
                    ? recentAnalyses.map(a => a.score || a.ats_score || 0)
                    : [0];

                window._recentChartInstance = new Chart(recentCanvas, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'ATS Score',
                            data: scores,
                            backgroundColor: '#C8FF3D',
                            borderRadius: 4,
                            maxBarThickness: 40
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        resizeDelay: 250,
                        animation: {
                            duration: 500
                        },
                        scales: {
                            y: { 
                                beginAtZero: true, 
                                max: 100,
                                grid: { color: 'rgba(244, 241, 232, 0.06)' },
                                ticks: { color: '#6F756F', font: { family: 'Inter', size: 11 } }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { color: '#6F756F', font: { family: 'Inter', size: 11 } }
                            }
                        },
                        plugins: {
                            legend: { display: false }
                        }
                    }
                });
            }
        })
        .catch(err => console.error("Error fetching dashboard stats:", err));
});
