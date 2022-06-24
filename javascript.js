async function control(pump, fan) 
{
    
    await fetch("/control" + "?pump_status=" + pump + "&" + "fan_status=" + fan)
    
    let response  = await fetch("/control");
    let common_data = await response.json();
    let pump_state = common_data[0]; //[0] pump control; [1] fan control
    let fan_state = common_data[1];
    
    document.getElementById('pump1').innerHTML = "Motor Pump: " + pump_state;
    document.getElementById('fan1').innerHTML = "Fan: " + fan_state;
    
}



async function drawChartData() {
    let result = await fetch("\chart");
    let common_data = await result.json();
    chartDataHumid =  common_data.filter((item, index) => index  % 2 );
    chartDataTemper = common_data.filter((item, index) => index  % 2 != true);

    //console.log(chartDataTemper)

    const CHART_COLORS = {
        red: 'rgb(255, 99, 132)',
        orange: 'rgb(255, 159, 64)',
        yellow: 'rgb(255, 205, 86)',
        green: 'rgb(75, 192, 192)',
        blue: 'rgb(54, 162, 235)',
        purple: 'rgb(153, 102, 255)',
        grey: 'rgb(201, 203, 207)'
      };

    const config = {
        type: 'line',
        inputs: {
            min: -200,
            max: 60,
            count: 12,
            decimals: 2,
            continuity: 1
          },
        data:
        {
            datasets: 
            [{
                label: 'Temperature in 24 hrs',
                data: chartDataTemper,
                cubicInterpolationMode: 'monotone',
                borderColor: CHART_COLORS.blue,
                fill: false,
              
             },

             {
                label: 'Humidity in 24 hrs',
                data: chartDataHumid,
                cubicInterpolationMode: 'monotone',
                borderColor: CHART_COLORS.green,
                fill: false,
              
             },


            
            ],
              labels: ['0hr', '1hr', '2hr', '3hr', '4hr', '5hr', '6hr', '7hr', '8hr', '9hr', '10hr', '11hr', '12hr', '13hr', '14hr', '15hr', '16hr', '17hr', '18hr', '19hr', '20hr', '21hr', 
              '22hr', '23hr']


        },
        options: {
           scales: {
              y: { // defining min and max so hiding the dataset does not change scale range
                min: 0
                
              }
            }
          }


    }


    const ctx = document.getElementById('dataChart').getContext('2d');
    const myChart = new Chart(ctx, config)
}
        
        


async function get_data() {
    let response  = await fetch("/data");
    let common_data = await response.json();
    let temper = common_data[0];
    let humid = common_data[1];
    document.getElementById("gauge_temp").setAttribute("data-value", temper)
    document.getElementById("humid_temp").setAttribute("data-value", humid.toString())
    
    // document.getElementById('temp').innerHTML = temper;
    // document.getElementById('hum').innerHTML = humid;
    
    
}

window.onload = function() {
    
    setInterval(get_data, 3000);
    drawChartData();
}
 
 



// function getCookie(name) {
//    return (name = new RegExp('(?:^|;\\s*)' + ('' + name).replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&') + '=([^;]*)').exec(document.cookie)) && name[1];
//}
                
//function showMessage() {
    // document.getElementById('temp').innerHTML = getCookie('temp');
    // document.getElementById('hum').innerHTML = getCookie('hum');
//}