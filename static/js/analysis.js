document.addEventListener('DOMContentLoaded', () => {
    // Animate score circle
    const scoreVal = document.getElementById('final-score');
    if (scoreVal) {
        const target = parseFloat(scoreVal.getAttribute('data-score')) || 0;
        const circlePath = document.querySelector('.score-circle-path');
        
        // 283 is the circumference of r=45 (2 * pi * 45)
        const circumference = 283;
        const offset = circumference - (circumference * target) / 100;
        
        setTimeout(() => {
            if(circlePath) {
                circlePath.style.strokeDashoffset = offset;
                
                // color based on score
                if (target >= 90) circlePath.style.stroke = '#10b981'; // Excellent
                else if (target >= 75) circlePath.style.stroke = '#06b6d4'; // Good
                else if (target >= 60) circlePath.style.stroke = '#f59e0b'; // Fair
                else circlePath.style.stroke = '#ef4444'; // Poor
            }
        }, 100);
        
        // Count up animation
        let current = 0;
        const duration = 1500;
        const interval = 20;
        const step = target / (duration / interval);
        
        if (target > 0) {
            const timer = setInterval(() => {
                current += step;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                scoreVal.textContent = Math.round(current);
            }, interval);
        }
    }
    
    // Animate progress bars
    const bars = document.querySelectorAll('.progress-bar-fill');
    bars.forEach(bar => {
        setTimeout(() => {
            const width = bar.getAttribute('data-width') || '0';
            bar.style.width = width + '%';
        }, 300);
    });
    
    // Keyword Chart
    const ctx = document.getElementById('keywordChart');
    if (ctx && typeof window.matchedKeywordsCount !== 'undefined') {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Matched', 'Missing'],
                datasets: [{
                    label: 'Keywords',
                    data: [window.matchedKeywordsCount, window.missingKeywordsCount],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
    
    // Compare Radar Chart
    const compareCtx = document.getElementById('compareChart');
    if (compareCtx && typeof window.compareData1 !== 'undefined') {
        const d1 = window.compareData1;
        const d2 = window.compareData2;
        
        if (d1 && d2) {
            new Chart(compareCtx, {
                type: 'radar',
                data: {
                    labels: ['Keyword Match', 'Skills Match', 'Semantic', 'Experience', 'Education'],
                    datasets: [
                        {
                            label: 'Analysis 1',
                            data: [d1.keyword_match || 0, d1.skills_match || 0, d1.semantic_similarity || 0, d1.experience || 0, d1.education || 0],
                            borderColor: '#6366f1',
                            backgroundColor: 'rgba(99, 102, 241, 0.2)',
                            pointBackgroundColor: '#6366f1'
                        },
                        {
                            label: 'Analysis 2',
                            data: [d2.keyword_match || 0, d2.skills_match || 0, d2.semantic_similarity || 0, d2.experience || 0, d2.education || 0],
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.2)',
                            pointBackgroundColor: '#10b981'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            angleLines: { display: true },
                            suggestedMin: 0,
                            suggestedMax: 100
                        }
                    }
                }
            });
        }
    }
});
