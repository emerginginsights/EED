var ctx = document.getElementById('el-consumption__chart').getContext("2d");
    var thirdGradient = ctx.createLinearGradient(0, 0, 0, 400);
    var fourthGradient = ctx.createLinearGradient(0, 0, 0, 400);
thirdGradient.addColorStop(0, 'rgba(252, 119, 48, 1)');
thirdGradient.addColorStop(0.2, 'rgba(252, 119, 48, 0.3)');
thirdGradient.addColorStop(0.4, 'rgba(252, 119, 48, 0.15)');
fourthGradient.addColorStop(0, 'rgba(55, 204, 147, 1)');
fourthGradient.addColorStop(0.2, 'rgba(55, 204, 147, 0.7)');
fourthGradient.addColorStop(0.3, 'rgba(55, 204, 147, 0.4)');
fourthGradient.addColorStop(0.4, 'rgba(55, 204, 147, 0.2)');
var elConsumptionChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['1910', '1920', '1930', '1940', '1950', '1960', '1990', '2000', '',],
        datasets: [
        {
            label: '# of Votes',
            data:  [0, 1.5, 2, 1.9, 2.3, 2.6, 3, 3.1, 3.4],
            backgroundColor: fourthGradient,
            borderColor: [
                'rgba(55, 204, 147, 1)',
            ],
            borderWidth: 5},
        {
            label: '# of Votes',
            data: [0, 3, 4, 3.8, 4.6, 5.2, 6, 6.2, 6.8 ],
            backgroundColor: thirdGradient,
            borderColor: [
                'rgba(252, 119, 48, 1)',
            ],
            borderWidth: 5
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
                    fontSize: 16,
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
                    fontSize: 16,
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