var ctx = document.getElementById('GDP-and-GNI__chart-mini').getContext("2d");
    var tenthGradientMini = ctx.createLinearGradient(0, 0, 0, 400);
    var eleventhGradientMini = ctx.createLinearGradient(0, 0, 0, 400);
tenthGradientMini.addColorStop(0, '#37CC93');
eleventhGradientMini.addColorStop(0, '#2772FF');
var gpdAndGniChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['1910', '1920', '1930', '1940', '1950', '1960', '1990', '2000', '',],
        datasets: [
        {
            barPercentage: 0.9,
            categoryPercentage: 0.4,
            data:  [1.5, 2, 1.9, 2.3, 2.6, 3, 3.1, 3.4, 3.5],
            backgroundColor: eleventhGradientMini,
            borderWidth: 1},
        {
            barPercentage: 0.9,
            categoryPercentage: 0.4,
            data: [3, 4, 3.8, 4.6, 5.2, 6, 6.2, 6.8, 6.9 ],
            backgroundColor: tenthGradientMini,
            borderWidth: 1
        },
        ]
    },
    options: {
        cornerRadius: 20,
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
                    beginAtZero: true,
               }
            }],
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

