// Main JS for SOC Dashboard

document.addEventListener('DOMContentLoaded', function () {

    // Check if we are on dashboard
    if (document.getElementById('trafficChart')) {
        initDashboardCharts();
        startDataPolling();
    }

    // Check if we are on map page
    if (document.getElementById('map')) {
        initMap();
    }

});

function initDashboardCharts() {
    const ctxTraffic = document.getElementById('trafficChart').getContext('2d');
    const trafficChart = new Chart(ctxTraffic, {
        type: 'line',
        data: {
            labels: Array(10).fill(''),
            datasets: [{
                label: 'Requests/sec',
                data: Array(10).fill(0),
                borderColor: '#00FF9F',
                backgroundColor: 'rgba(0, 255, 159, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: false },
                y: { grid: { color: '#333' } }
            }
        }
    });

    // Simulating chart update with simulated traffic for visual effect
    setInterval(() => {
        const data = trafficChart.data.datasets[0].data;
        data.push(Math.floor(Math.random() * 50) + 10);
        data.shift();
        trafficChart.update();
    }, 2000);

    // Initialize Attack Distribution Chart
    const ctxAttack = document.getElementById('attackTypeChart').getContext('2d');
    window.attackTypeChart = new Chart(ctxAttack, {
        type: 'doughnut',
        data: {
            labels: ['Brute Force', 'DDoS', 'Port Scan', 'Malware', 'Normal'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: ['#FF3B3B', '#FFD700', '#00BFFF', '#FF00FF', '#00FF9F'],
                borderColor: '#121212'
            }]
        },
        options: {
            responsive: true,
            plugins: { position: 'right' }
        }
    });
}

function startDataPolling() {
    setInterval(() => {
        fetch('/api/alerts')
            .then(res => res.json())
            .then(data => {
                updateRecentAlertsTable(data);
            })
            .catch(err => console.error(err));

        fetch('/api/stats')
            .then(res => res.json())
            .then(data => {
                document.getElementById('total-alerts').innerText = data.total;
                document.getElementById('critical-alerts').innerText = data.critical;

                // Update Attack Type Chart
                if (window.attackTypeChart && data.attack_types) {
                    const chart = window.attackTypeChart;
                    // Map API data to chart labels
                    const stats = data.attack_types;
                    const newData = [
                        stats['brute_force'] || 0,
                        stats['ddos'] || 0,
                        stats['port_scan'] || 0,
                        stats['malware'] || 0,
                        stats['normal'] || 0
                    ];
                    chart.data.datasets[0].data = newData;
                    chart.update();
                }
            });

    }, 5000);
}

function updateRecentAlertsTable(alerts) {
    const tbody = document.querySelector('#dashboard-table tbody');
    if (!tbody) return;

    let html = '';
    alerts.slice(0, 8).forEach(alert => {
        const riskClass = alert.risk > 80 ? 'high' : (alert.risk > 50 ? 'medium' : 'low');
        const riskBarColor = alert.risk > 80 ? '#FF3B3B' : (alert.risk > 50 ? '#FFD700' : '#00FF9F');

        html += `
            <tr class="alert-row risk-${riskClass}">
                <td>${alert.timestamp.split(' ')[1]}</td>
                <td class="mono">${alert.ip}</td>
                <td>${alert.country || 'Unknown'}</td>
                <td><span class="badge">${alert.type}</span></td>
                <td>
                    <div class="risk-meter">
                        <div class="bar" style="width: ${alert.risk}%; background: ${riskBarColor}"></div>
                        <span class="val">${alert.risk}</span>
                    </div>
                </td>
                <td><a href="/incident/${alert.id}" class="btn-xs">Inspect</a></td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

function initMap() {
    // If mapData is available globally (injected by template)
    if (typeof mapData === 'undefined') return;

    var map = L.map('map').setView([20, 0], 2);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    mapData.forEach(point => {
        const color = point.risk > 80 ? '#FF3B3B' : '#FFD700';
        L.circleMarker([point.lat, point.lon], {
            radius: 8,
            fillColor: color,
            color: '#000',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        })
            .bindPopup(`<b>IP:</b> ${point.ip}<br><b>Risk:</b> ${point.risk}`)
            .addTo(map);
    });
}
