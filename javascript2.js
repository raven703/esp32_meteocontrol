

function autoModeCtrl(){
    let auto = document.getElementById('autoMode').checked;
    if (auto) { 
      
      fetch("/control" + "?auto_mode=ON&device1=False&device2=False");
  
    } else {
      fetch("/control" + "?auto_mode=OFF&device1=False&device2=False");
      
    }
    
  }


function control(device, status) {
    if (device == 'device1') {
        fetch("/control" + "?device1=" + status + "&" + "device2=false" + "&auto_mode=None")
    }

    if (device == 'device2') {
        fetch("/control" + "?device2=" + status + "&" + "device1=false" + "&auto_mode=None")
    }

}


async function getDataFromServer() {
    
   // let response = await fetch("config.json"); // load config from server
   // let config = await response.json();


// start Server Side Events to get data from server
// and show it on gauges
    let source = new EventSource("/progress");
   
  
      source.onmessage = function (event) {	
  
      data = JSON.parse(event.data);
  
   
      
      // get sensors value from SSE
      let temper = data['Sensors']['temp'];
      let humid = data['Sensors']['hum'];
      let soil = data['Sensors']['soil'];
      let autoModeStatus = data['Control']['auto'];
      let device1Status = data['Control']['device1'];
      let device2Status = data['Control']['device2'];
      let device1_name = data['Names']['device1_name'];
      let device2_name = data['Names']['device2_name'];
      let time = data['Time'];
      let date = data['Date'];
         
      document.getElementById("temperature").innerHTML = temper;
      document.getElementById("humidity").innerHTML = humid;
      document.getElementById("soil_hum").innerHTML = soil;
      document.getElementById("time").innerHTML = time;
      document.getElementById("date").innerHTML = date;
        
      document.getElementById("device1_name_card").innerHTML = device1_name;
      document.getElementById("device2_name_card").innerHTML = device2_name;
       
        if (device1Status) {
        document.getElementById("device_1_on").classList.add("btn", "btn-success");
        document.getElementById("device_1_off").classList.remove("btn", "btn-danger");
        } else {
        document.getElementById("device_1_on").classList.remove("btn", "btn-success");
        document.getElementById("device_1_off").classList.add("btn", "btn-danger");
        }

        if (device2Status) {
        document.getElementById("device_2_on").classList.add("btn", "btn-success");
        document.getElementById("device_2_off").classList.remove("btn", "btn-danger");
        } else {
        document.getElementById("device_2_on").classList.remove("btn", "btn-success");
        document.getElementById("device_2_off").classList.add("btn", "btn-danger");
        }
               
      }
  
      }
       

      
// functions for settings


function convertFormData(formData) {

  let object = {};
  formData.forEach(function(value, key){
      object[key] = value;
  });
  let result = JSON.stringify(object);
  return JSON.parse(result);
  
  
  }
  
  
  function handleGrow_box_settings(event) {
      event.preventDefault();
      params = convertFormData(new FormData(grow_box_settings));
  
      let temper = params['temper'];
      let humid_low = params['humid_low'];
      let humid_high = params['humid_high'];
      let soil = params['soil'];
      let run_time = params['run_time']
      let period_time = params['period_time']
      let dev_name1 = sessionStorage.getItem('device1_name');
      let dev_name2 = sessionStorage.getItem('device2_name');
      document.getElementById('autoMode').checked
      let autoMode = document.getElementById('autoMode').checked;
      
  
     
      
      fetch(`/config.json?save=1&h_temper=${temper}&th_humid_low=${humid_low}&th_humid_high=${humid_high}&th_soil=${soil}\
  &dev_name1=${dev_name1}&dev_name2=${dev_name2}&auto=${autoMode}&run_time=${run_time}&period_time=${period_time}`);
  alert('Settings saved');
  
  
     //fetch("/config.json" + "?save=1" + 
     // )
     // config.json?save=1&h_temper=30&th_humid_low=60&th_humid_high=70&th_soil=190&th_lamp=OFF&dev_name1=test1&dev_name2=test2
             
        }
  
  function  handleDevice_name(event) {
     
      event.preventDefault()
      params = convertFormData(new FormData(device_name));
      let temper = sessionStorage.getItem('temper');
      let humid_low = sessionStorage.getItem('hum_low');
      let humid_high = sessionStorage.getItem('hum_max');
      let soil = sessionStorage.getItem('soil_meter');
      let dev_name1 = params['device1_name'];
      let dev_name2 = params['device2_name'];
      let time = params['time'];
      let date = params['date'];
      
      fetch(`/config.json?save=1&h_temper=${temper}&th_humid_low=${humid_low}&th_humid_high=${humid_high}&th_soil=${soil}\
      &dev_name1=${dev_name1}&dev_name2=${dev_name2}&dev_time=${time}&dev_date=${date}`);
      alert('Settings saved');
  
           
        }
  
  
  
  function handleWifi_setup(event) {
      event.preventDefault()
      let wifi_mode='false'
      params = convertFormData(new FormData(wifi_setup));
  
  
      if (document.getElementById('station_mode').checked) {
      
          wifi_mode = 'station';
      }
      else {
        
          wifi_mode = 'point';
      }
      
      fetch(`/control?wifi=${wifi_mode}&ssid=${params['ssid']}&ssid_pass=${params['ssid_pass']}`);
      alert('Settings saved');
      
  }
  
  
  
  async function show_config_data () {
     let response = await fetch("config.json"); // load config from server
     let config = await response.json();

     let boot_ini = await fetch('boot_ini.json');
     let wifi = await boot_ini.json();
  
     sessionStorage.setItem('temper', config['temper'])
     sessionStorage.setItem('hum_low', config['humid'][0]);
     sessionStorage.setItem('hum_max', config['humid'][1]);
     sessionStorage.setItem('soil_meter', config['soil'])
     sessionStorage.setItem('device1_name', config['device1_name'])
     sessionStorage.setItem('device2_name', config['device2_name'])
      
      //{"auto": "False", temper: '30', humid: Array(2), soil: '190', device1_name: 'test1', device2_name: 'test2', …}
      document.getElementById('temp_max').value = config['temper'];
      document.getElementById('hum_low').value = config['humid'][0];
      document.getElementById('hum_max').value = config['humid'][1];
      document.getElementById('soil_meter').value = config['soil'];
      document.getElementById('device1_name').value = config['device1_name'];
      document.getElementById('device2_name').value = config['device2_name'];
      document.getElementById('ssid').value = wifi['SSID']
      document.getElementById('run_time').value = config['dev2_runtime']
      document.getElementById('period_time').value = config['dev2_period']


      if (wifi['DEFAULT_WIFI_MODE'] == 'station') {
        document.getElementById('station_mode').checked = true
        document.getElementById('point_mode').checked = false

      } else {
        document.getElementById('point_mode').checked = true
        document.getElementById('station_mode').checked = false
      }


      if (config['auto'] == 'True') {
          document.getElementById("autoMode").checked = true;
      } else {
          document.getElementById("autoMode").checked = false;
      }
      
   }

   // end settings block
  
  

window.onload = function() {
   
  document.getElementById('grow_box_settings').addEventListener('submit', handleGrow_box_settings);
  document.getElementById('device_name').addEventListener('submit', handleDevice_name);
  document.getElementById('wifi_setup').addEventListener('submit', handleWifi_setup);
  show_config_data(); 
  getDataFromServer();

    
   
  }
   