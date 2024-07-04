function createGauge(ctx, value, min, max) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, max - value],
                backgroundColor: ['#4caf50', '#ddd'],
                borderWidth: 0
            }]
        },
        options: {
            circumference: Math.PI,
            rotation: Math.PI,
            cutout: '75%',
            plugins: {
                tooltip: { enabled: false },
                legend: { display: false }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const voltageCtx = document.getElementById('voltageCanvas').getContext('2d');
    const currentCtx = document.getElementById('currentCanvas').getContext('2d');
    const powerFactorCtx = document.getElementById('powerFactorCanvas').getContext('2d');
    const powerCtx = document.getElementById('powerCanvas').getContext('2d');

    createGauge(voltageCtx, 120, 0, 250);
    createGauge(currentCtx, 5, 0, 10);
    createGauge(powerFactorCtx, 0.8, 0, 1);
    createGauge(powerCtx, 150, 0, 250);

    const loadStatusButton = document.getElementById('loadStatusButton');
    loadStatusButton.addEventListener('click', function () {
        if (loadStatusButton.textContent === 'Load Active') {
            loadStatusButton.textContent = 'Load Deactivated';
            loadStatusButton.classList.add('deactivated');
        } else {
            loadStatusButton.textContent = 'Load Active';
            loadStatusButton.classList.remove('deactivated');
        }
    });
});
