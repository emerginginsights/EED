var ctx = document.getElementById('methan__chart').getContext("2d");
var co2Chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['', ''],
        datasets: [{
        data: [75, 25],
        borderWidth: 0,
        backgroundColor: ['#F5D66B', 'rgba(252, 119, 48, 1)']
        }],
        
    },
    options: {
        maintainAspectRatio: false,
        elements: {
                    point:{
                        radius: 0
                    }
                },
        responsive: true,
        legend: {
           display: false,
        },
        rotation: -1 * Math.PI,
        cutoutPercentage: 37.5,
    }
});

let stat5 = co2Chart.config.data.datasets[0].data[0];
let stat6 = co2Chart.config.data.datasets[0].data[1]

let legendValue5 = document.getElementById('stat-item-5');
legendValue5.innerHTML = `${stat5}%`;
let legendValue6 = document.getElementById('stat-item-6');
legendValue6.innerHTML = `${stat6}%`;