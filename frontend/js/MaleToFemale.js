var ctx = document.getElementById('male-to-female__chart').getContext("2d");
var maleToFemaleChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['', ''],
        datasets: [{
        data: [75, 25],
        borderWidth: 0,
        backgroundColor: ['#A819E8','#F4D5FF']
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

let stat1 = maleToFemaleChart.config.data.datasets[0].data[0];
let stat2 = maleToFemaleChart.config.data.datasets[0].data[1]

let legendValue1 = document.getElementById('stat-item-1');
legendValue1.innerHTML = `${stat1}%`;
let legendValue2 = document.getElementById('stat-item-2');
legendValue2.innerHTML = `${stat2}%`;