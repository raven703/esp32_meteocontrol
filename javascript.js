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
    chartDataHumid =  common_data["humid"];
    chartDataTemper = common_data["temper"];
    chartDataSoil = common_data["soil"];
    chartDataTime = common_data["time"];
    drawChartData2(chartDataSoil, chartDataTime)
    
    
    
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
              labels: chartDataTime //['0hr', '1hr', '2hr', '3hr', '4hr', '5hr', '6hr', '7hr', '8hr', '9hr', '10hr', '11hr', '12hr', '13hr', '14hr', '15hr', '16hr', '17hr', '18hr', '19hr', '20hr', '21hr', 
                                    //'22hr', '23hr']


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
        
 
async function drawChartData2(soilData, timeData) {
  
  
  
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
          [
           {
            label: 'Soil humidity in 24 hrs, less is better ',
            data: chartDataSoil,
            cubicInterpolationMode: 'monotone',
            borderColor: CHART_COLORS.red,
            fill: false,
          
         },
     
          ],
            labels: timeData //['0hr', '1hr', '2hr', '3hr', '4hr', '5hr', '6hr', '7hr', '8hr', '9hr', '10hr', '11hr', '12hr', '13hr', '14hr', '15hr', '16hr', '17hr', '18hr', '19hr', '20hr', '21hr', 
            //'22hr', '23hr']


      },
      options: {
         scales: {
            y: { // defining min and max so hiding the dataset does not change scale range
              min: 0
              
            }
          }
        }


  }


  const ctx2 = document.getElementById('dataChart2').getContext('2d');
  const myChart = new Chart(ctx2, config)
}




async function getDataFromServer() {
    let response  = await fetch("/data");
    let common_data = await response.json();
    let temper = common_data[0];
    let humid = common_data[1];
    let soil = common_data[2];
    document.getElementById("gauge_temp").setAttribute("data-value", temper)
    document.getElementById("humid_temp").setAttribute("data-value", humid.toString())
    document.getElementById("soil").setAttribute("data-value", soil)

    // update button status
    let button_respone = await fetch("/control"); // [motor, fan]
    let button_data = await button_respone.json();
    let pump_state = button_data[0]; //[0] pump control; [1] fan control
    let fan_state = button_data[1];     
    document.getElementById('pump1').innerHTML = "Motor Pump: " + pump_state;
    document.getElementById('fan1').innerHTML = "Fan: " + fan_state;

    
    // document.getElementById('temp').innerHTML = temper;
    // document.getElementById('hum').innerHTML = humid;
    
    
}



window.onload = function() {
    
    setInterval(getDataFromServer, 3000);
    drawChartData();
}
 
 

