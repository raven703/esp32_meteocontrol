//function setServerSideEvents() {
//let source = new EventSource("/progress");

	//source.onmessage = function (event) {	

    //data = JSON.parse(event.data);

	//	console.log(data['Sensors']['hum']);
  //  console.log(data['Control']);

	//}
//}



function control(pump, fan) 
{
    
  let auto = document.getElementById('autoMode').checked;
  let auto_mode = "OFF"

  if (auto) { 
    auto_mode = "ON";

  } else {
    auto_mode="OFF";
 }

    // put control data to web server
    fetch("/control" + "?pump_status=" + pump + "&" + "fan_status=" + fan + "&" + "auto_mode=" + auto_mode )
    
    // get states from localStorage 
    
    let pump_state = localStorage.getItem('pump_state');
    let fan_state = localStorage.getItem('fan_state'); 
    if (fan_state == null ){
      console.log("DDDD")
    }
    let autoMode = localStorage.getItem('autoMode');
       
    document.getElementById('pump1').innerHTML = "Auto Lamp: " + pump_state;
    document.getElementById('fan1').innerHTML = "Fan: " + fan_state;
    
}

// func to control automode from webpage
async function autoMode(){
  let auto = document.getElementById('autoMode').checked;
  if (auto) { 
    
    await fetch("/control" + "?auto_mode=ON");

  } else {
    await fetch("/control" + "?auto_mode=OFF");
    
  }
  
}

async function showLog(log_type) 
{
  if (log_type == "data") {
    let common_data = await (await fetch("/log2.json")).json();
    chartDataHumid =  common_data["humid"];
    chartDataTemper = common_data["temper"];
    chartDataSoil = common_data["soil"];
    chartDataTime = common_data["time"];
    

    document.getElementById('log-field').innerHTML = "Temp: " + "\n" + chartDataTemper + "\n" + "RH: " + "\n" + chartDataHumid + "\n" + "SRH: " + "\n" + chartDataSoil;
  } else if (log_type == "auto") {
    document.getElementById('log-field').innerHTML = await (await fetch("/log.txt")).text();
    
  }



    // let response  = await fetch("/control");
    // let common_data = await response.json();
    // let pump_state = common_data[0]; //[0] pump control; [1] fan control
    // let fan_state = common_data[1];
    
    document.getElementById('pump1').innerHTML = "Auto Lamp: " + pump_state;
    document.getElementById('fan1').innerHTML = "Fan: " + fan_state;
    
}



async function drawChartData() {
// set checkbox

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

  let source = new EventSource("/progress");

	source.onmessage = function (event) {	

    data = JSON.parse(event.data);

		// console.log(data['Sensors']['hum']);
    // console.log(data['Control']);
    
    // get sensors value from SSE
    let temper = data['Sensors']['temp'];
    let humid = data['Sensors']['hum']
    let soil = data['Sensors']['soil']
    let autoMode = data['Control']['auto']
    
  



    // set corresponding values on web page
    if (autoMode == 'ON') {
      document.getElementById("autoMode").checked = true;
    }
    else {
      document.getElementById("autoMode").checked = false;
    }
    
        document.getElementById("gauge_temp").setAttribute("data-value", temper)
        document.getElementById("humid_temp").setAttribute("data-value", humid.toString())
        document.getElementById("soil").setAttribute("data-value", soil)

    // get buttons status from SSE

    let pump_state = data['Control']['lamp'];
    let fan_state = data['Control']['fan'];     
    console.log("fan_state is", fan_state)

    document.getElementById('pump1').innerHTML = "Auto Lamp: " + pump_state;
    document.getElementById('fan1').innerHTML = "Fan: " + fan_state;

    // put all values to localStorage
      localStorage.setItem('temper',temper.toString())
      localStorage.setItem('humid',humid.toString())
      localStorage.setItem('soil',soil.toString())
      localStorage.setItem('autoMode',autoMode.toString())
      localStorage.setItem('pump_state',pump_state.toString())
      localStorage.setItem('fan_state',fan_state.toString())


  } // end of SSE script

    // update button status
    

    
    // document.getElementById('temp').innerHTML = temper;
    // document.getElementById('hum').innerHTML = humid;
    
    
}



window.onload = function() {
  
  getDataFromServer();
  drawChartData();
  // setInterval(getDataFromServer, 3000);
}
 
 

