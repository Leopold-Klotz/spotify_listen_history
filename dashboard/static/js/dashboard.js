// Initialize hourly activity chart
const hourlyChart = new Chart(
    document.getElementById('hourly-chart'),
    {
        type: 'bar',
        data: {
            labels: Array.from({length: 24}, (_, i) => `${i}:00`),
            datasets: [{
                label: 'Tracks Played',
                data: [],
                backgroundColor: 'rgba(29, 185, 84, 0.5)',  // Spotify green
                borderColor: 'rgb(29, 185, 84)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    }
);

// Update dashboard with new stats
function updateStats(stats) {
    // Update summary cards
    document.getElementById('total-tracks').textContent = stats.total_tracks;
    document.getElementById('unique-tracks').textContent = stats.unique_tracks;
    document.getElementById('total-duration').textContent = `${stats.total_duration_hrs.toFixed(1)}h`;

    // Update top artists
    const artistsList = document.getElementById('top-artists');
    artistsList.innerHTML = Object.entries(stats.top_artists)
        .map(([artist, count]) => `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                ${artist}
                <span class="badge bg-primary rounded-pill">${count}</span>
            </div>
        `).join('');

    // Update top tracks
    const tracksList = document.getElementById('top-tracks');
    tracksList.innerHTML = Object.entries(stats.top_tracks)
        .map(([trackInfo, count]) => {
            const [track, artist] = trackInfo.split(',');
            return `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    ${track} - ${artist}
                    <span class="badge bg-primary rounded-pill">${count}</span>
                </div>
            `;
        }).join('');

    // Update top albums
    const albumsList = document.getElementById('top-albums');
    albumsList.innerHTML = Object.entries(stats.top_albums)
        .map(([album, count]) => `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                ${album}
                <span class="badge bg-primary rounded-pill">${count}</span>
            </div>
        `).join('');

    // Update hourly chart
    const hourlyData = Array.from({length: 24}, (_, i) => stats.hourly_activity[i] || 0);
    hourlyChart.data.datasets[0].data = hourlyData;
    hourlyChart.update();
}

// Handle time period selection
document.querySelectorAll('[data-period]').forEach(button => {
    button.addEventListener('click', async (e) => {
        // Update button states
        document.querySelectorAll('[data-period]').forEach(btn => {
            btn.classList.remove('active');
        });
        e.target.classList.add('active');

        // Fetch and update stats
        const period = e.target.dataset.period;
        try {
            const response = await fetch(`/api/stats/${period}`);
            const stats = await response.json();
            updateStats(stats);
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    });
}); 