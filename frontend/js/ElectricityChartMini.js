var ctx = document.getElementById('electricity__chart-mini').getContext("2d");
    var firstGradientMini = ctx.createLinearGradient(0, 0, 0, 400);
    var secondGradientMini = ctx.createLinearGradient(0, 0, 0, 400);
firstGradientMini.addColorStop(0, '#76EFFF');
secondGradientMini.addColorStop(0, '#2772FF');
var electricityChartMini = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['1910', '1920', '1930', '1940', '1950', '1960', '1990', '2000', '',],
        datasets: [
        {
            label: '# of Votes',
            data:  [0, 1.5, 2, 1.9, 2.3, 2.6, 3, 3.1, 3.4],
            backgroundColor: secondGradientMini,
            borderColor: [
                '#8888EA',
            ],
            borderWidth: 1},
        {
            label: '# of Votes',
            data: [0, 3, 4, 3.8, 4.6, 5.2, 6, 6.2, 6.8 ],
            backgroundColor: firstGradientMini,
            borderColor: [
                '#8888EA',
            ],
            borderWidth: 1
        },
        ]
    },
    options: {
        scales: {
           xAxes: [{
               gridLines: {
                  drawOnChartArea: false,
                  color: 'rgba(255, 255, 255, 0.2)',
                  zeroLineColor: 'rgba(255, 255, 255, 0.2)',
               },
               ticks: {
                    fontSize: 8,
                    fontFamily: 'Lato',
                    fontColor: "#fff",
               }
            }],
            yAxes: [{
               gridLines: {
                  drawOnChartArea: false,
                  color: 'rgba(255, 255, 255, 0.2)',
                  zeroLineColor: 'rgba(255, 255, 255, 0.2)',
               },
               ticks: {
                    fontSize: 8,
                    fontFamily: 'Lato',
                    fontColor: "#fff",
               }
            }]
        },
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
    }
});