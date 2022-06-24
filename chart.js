$(function() {


    let attrdata  = $("#chartData").attr('data-chart');
    

    if (typeof attrdata !== 'undefined') {
        let data2 = '{' + JSON.parse(attrdata) + '}'
        let dataset = JSON.parse(data2)


        let chartData = dataset["c_data"];
	    let chartLabels = dataset["labels"];
        let chartColors = dataset["colors"];

        drawChart(chartData, chartLabels, chartColors);
    }

})



function drawChart(chartData, chartLabels, chartColors)
{
    const ctx = document.getElementById('myChart').getContext('2d');

    const myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartLabels,
            datasets: [{
                data: chartData,
                backgroundColor: chartColors,
                borderColor: ['rgba(255, 255, 255, 0.2)']
            }],
            labels: chartLabels
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}