import time
import uftpd

import uasyncio as asyncio

import json

from microdot_asyncio import Microdot, redirect, send_file, Response, Request
from machine import Pin, RTC, ADC, SoftI2C as I2C, Timer
from htu21d import *
from device import *

DEVICE1_TIMER = 20 #timer in seconds, switch off after this period
DEVICE2_TIMER = 10 #timer in seconds, switch off after this period
DEVICE2_PERIOD_TIMER = 18000 #in seconds, period for pump activation (device2)


rtc = RTC()

i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000) #setup I2C
display = SSD1306_I2C(128, 32, i2c) #init oled driver
Request.max_content_length = 1024 * 1024
Request.max_body_length = 1024 * 1024



def getRtcTime():
    date_str = "{2:02d}.{1:02d}.{0:4d}".format(*rtc.datetime())
    time_str = "{4:02d}:{5:02d}".format(*rtc.datetime())
    return [date_str, time_str]  



class stream(): #async generator for server side events
    def __init__(self):

        self.data = { 'Sensors': {'hum':'0',
                      'temp':0,
                      'soil':0}, 

         'Control': {'device1':0,
                     'device2':0,
                     'auto':0 },
         'Names': {'device1_name': 'noname1',
                   'device2_name': 'noname2'},
         'Time': {0},
         'Date': {0}
         }

        with open("config.json", "r") as json_data: #load config from json file and read names for devices
             self.config = json.load(json_data)
        self.data['Names']['device1_name'] = device1.name = self.config['device1_name']
        self.data['Names']['device2_name'] = device2.name = self.config['device2_name']
         
        if "True" in self.config['auto']:
            autoModeCtrl.status = True
        else:
            autoModeCtrl.status = False

 

    def __aiter__(self):
        return self

    async def __anext__(self):
        

        self.data['Names']['device1_name'] = device1.name
        self.data['Names']['device2_name'] = device2.name

        self.data['Control']['auto'] = autoModeCtrl.status

        try:
            self.temper = round(gy21.temperature)
            gy21.LAST_VALUE_TEMP = self.temper
        except:
            #print('! exception ! TEMP Error')
            self.temper = gy21.LAST_VALUE_TEMP 

        try:
            self.hum = round(gy21.humidity)
            gy21.LAST_VALUE_HU = self.hum
        except:
           #print('! exception ! HUM Error')
           self.hum = gy21.LAST_VALUE_HU 

        date, current_time = getRtcTime()

        self.soil = soilMeter.read() / 10
        
        self.data['Sensors']['hum'] = self.hum
        self.data['Sensors']['temp'] = self.temper
        self.data['Sensors']['soil'] = self.soil
        
        self.data['Control']['device1'] = device1.running()
        self.data['Control']['device2'] = device2.running()
        self.data['Time'] = current_time
        self.data['Date'] = date
        await asyncio.sleep(1)
        return f"data: {json.dumps(self.data)}" + "\n\n"



        
        
# setup webserver
app = Microdot()


# 
gy21 = HTU21D(22,21)  #take temp and hum from sensor # HTU21D(scl, sda)

#setup devices
device1 = motorDevice(12, "device1") #fan
device2 = motorDevice(14, "device2") #pump

#setup soil sensor
soilMeter = ADC(Pin(34), atten=ADC.ATTN_11DB)

#setup automode control from Class
autoModeCtrl = autoModeControl()

#setup timer for display and debounce function

timer = Timer(0) #for display
pumpTimer = Timer(1) #timer for pump



def dispalySwitchOff(timer): #set timer for display off
    display.fill(0)
    display.show()


def button1_click_func(): #function for button1 
    if not device2.running() and Pin(13).value() == 1:
        
                
        try:
            temper = round(gy21.temperature)
            gy21.LAST_VALUE_TEMP = temper
        except:
            print('! exception ! TEMP Error')
            temper = gy21.LAST_VALUE_TEMP 

        try:
            hum = round(gy21.humidity)
            gy21.LAST_VALUE_HU = hum
        except:
           print('! exception ! HUM Error')
           hum = gy21.LAST_VALUE_HU 

    
        if button1.screen == 0:
            display.fill(0)
            display.text(f'auto mode: {autoModeCtrl.status}', 0, 0, 1)
            display.text(f'temp, C: {temper}', 0, 12, 1)
            display.text(f'hum, RH: {hum}', 0, 24, 1)
            display.show()
            button1.screen = 1      #set screen number  
        elif button1.screen == 1: 
            display.fill(0)
            display.text(f'Watering Status', 0, 0, 1)
            display.text(f'Soil: {autoModeCtrl.soilData} / {autoModeCtrl.th_soil}', 0, 12, 1)
            if autoModeCtrl.soilData > autoModeCtrl.th_soil:
                display.text(f'Need Water!', 0, 24, 1)
            else:
                display.text(f'Soil is OK', 0, 24, 1)
            display.show()
            button1.screen = 0    #set screen number   
        timer.init(mode=Timer.ONE_SHOT, period=5000, callback=dispalySwitchOff)

button1 = Button(Pin(13, Pin.IN, Pin.PULL_DOWN), callback=button1_click_func) #instatiate button object from device.py 


device1.stop()
device2.stop()


async def writeLog(): # write log for temp, humid and soil. Send data to /chart. Need to have empty .json file at first start. 
    # json format: 
    # data = {
        #        "temper": [],
        #        "humid": [],
        #        "soil": []
        #        "time": []
        #    }

    while True: 
        with open ("log2.json", "r") as f:
            data = json.load(f)
            date, current_time = getRtcTime()

        

        try:
            temper = round(gy21.temperature)
            gy21.LAST_VALUE_TEMP = temper
        except:
            print('! exception ! TEMP Error')
            temper = gy21.LAST_VALUE_TEMP 

        try:
            hum = round(gy21.humidity)
            gy21.LAST_VALUE_HU = hum
        except:
           print('! exception ! HUM Error')
           hum = gy21.LAST_VALUE_HU 

        soil = soilMeter.read()
        
        

        # write last value to the last index
        data["temper"].pop(0)
        data["temper"].append(int(temper))
        data["humid"].pop(0)
        data["humid"].append(int(hum))
        data["soil"].pop(0)
        data["soil"].append(int(soil /10 ))
        data["time"].pop(0)
        data["time"].append(current_time)

        #data_result = json.dumps(data)
        with open ("log2.json", "w") as f:
            json.dump(data, f)
           
          
        await asyncio.sleep(3200)


async def emergencyDeviceControl(): #counter for emerg shutdown DEVICE1 or DEVICE2 
    device1.isTimerSet = False
    device2.isTimerSet = False

    while True:


        if device1.running():
            time_now = time.time()
            print('Device1 autooff in: ', DEVICE1_TIMER - round(time_now - device1.startTime))
            
            if time_now - device1.startTime > DEVICE1_TIMER:
                print('time reached')
                device1.stop()


        if device2.running():
            time_now = time.time()
            print('Device2 autooff in: ', DEVICE2_TIMER - round(time_now - device2.startTime))
            
            if time_now - device2.startTime > DEVICE2_TIMER:
                print('time reached')
                device2.stop()
           
        await asyncio.sleep(2) 
            

        


async def deviceControl(): #control for device1 and device2. Can use auto control or manual
  
    write_request = True
    last_max_temper = 0
    last_max_hum = 0

    with open ("config.json", "r") as file:
        config = json.load(file)
 
       # set thresholds for autowork sensors from config file
       # set auto mode from config file
       # humid is list [low_value, high_value]
   
    th_temper = int(config["temper"])
    th_humid_low = int(config["humid"][0])
    th_humid_high = int(config["humid"][1])
    autoModeCtrl.th_soil = int(config["soil"])
  
    

    
    if "ON" or "True" in config['auto']:
        autoModeCtrl.status = True
    else:
        autoModeCtrl.status = False

    
    while True: 
        
        try:
            temper = round(gy21.temperature)
            gy21.LAST_VALUE_TEMP = temper
        except:
            #print('! exception ! TEMP Error')
            temper = gy21.LAST_VALUE_TEMP 

        try:
            hum = round(gy21.humidity)
            gy21.LAST_VALUE_HU = hum
        except:
           #print('! exception ! HUM Error')
           hum = gy21.LAST_VALUE_HU 

        if temper < th_temper:
            last_max_temper = 0
        if hum < th_humid_low:
            last_max_hum = 0
  
        with open ("log2.json", "r") as f:
                data = json.load(f)
        soil_data_len = len([i for i in data["soil"] if i>0])
        if soil_data_len > 0:
            soilData = int(sum(data["soil"][:-4:-1]) / len(data["soil"][:-4:-1]))
            autoModeCtrl.soilData = soilData #pass value to class
        
        
        autoMode = autoModeCtrl.status
        
    
        if autoMode:
          
            if temper > th_temper:
                #print("Temp exceed threshold")
                if temper > last_max_temper:
                    last_max_temper = temper
                    write_request = True

                # if not device1.running():
                #    device1.start()
            
                if write_request:
                    with open("log.txt", "w") as output:
                        output.write(f'Temp: {temper} {getRtcTime()} \n')
                    if temper > last_max_temper: 
                        write_request = True
                    else:
                        write_request = False

            if temper < th_temper: 
                
                #device1.stop()
                #print("Temp below threshold")
                write_request = True
            
            if hum > th_humid_high:
                if hum > last_max_hum:
                    last_max_hum = hum
                    write_request = True
                #print("Humidity exceed threshold")
                if not device1.running():                   
                    device1.start()
            
                if write_request:
                    with open("log.txt", "w") as output:
                        output.write(f'Hum: {hum} {getRtcTime()} \n')
                    if hum > last_max_hum: 
                        write_request = True
                    else:
                        write_request = False
           
            if hum < th_humid_low: # or temper < th_temper :
                #print("Humidity below threshold")
                device1.stop()
                write_request = True
 
            if soilData > autoModeCtrl.th_soil:
                print("raw soil sensor", soilMeter.read(), "ALERT NEED WATER !!!!")
                time_now = time.time()
                
                #print('DEVICE2_PERIOD_TIMER', DEVICE2_PERIOD_TIMER)
                if time_now - device2.periodStartTime < DEVICE2_PERIOD_TIMER:
                    
                    print('auto device2, waiting to start', DEVICE2_PERIOD_TIMER - (time_now - device2.periodStartTime))
                elif time_now - device2.periodStartTime > DEVICE2_PERIOD_TIMER:
                    print("starting")
                    device2.periodStartTime = time.time()
                    device2.start()


            else:
                write_request = True
        
        await asyncio.sleep(5)



@app.route('/progress', methods=["GET", "POST"]) #sending ServerSideEvents to browser
async def progress(request):
    
   return stream(), 200, {"Content-Type": "text/event-stream"}
   # return 'OK'




@app.route('/')
async def index(response):
    return send_file("index.html")


@app.route('/static/<path:path>')
async def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('static/' + path)

 
@app.route('/config.json', methods=['GET', 'POST'] ) #here we save and load config data to server
async def config(request):
    params = request.args #request args from GET
    # config.json?save=1&h_temper=30&th_humid_low=60&th_humid_high=70&th_soil=190&th_lamp=OFF&dev_name1=test1&dev_name2=test2 
    if "save" in params:

        config_data = {
           "auto": str(autoModeCtrl.status),
           "temper": params.get("h_temper") if params.get("h_temper") is not None else 0,
           "humid": [params.get('th_humid_low') if params.get('th_humid_low') is not None else 0, \
           params.get('th_humid_high') if params.get('th_humid_high') is not None else 0],
           "soil": int(params.get("th_soil")) if params.get("th_soil") is not None else 180,
           "lamp": params.get("th_lamp") if params.get("th_lamp") is not None else 0,
           "device1_name": params.get("dev_name1") if params.get("dev_name1") is not None else "noname1",
           "device2_name": params.get("dev_name2") if params.get("dev_name1") is not None else "noname2",
           "dev_time":params.get('dev_time'),
           "dev_date":params.get('dev_date') 

           }
        
        

        device1.name, device2.name = params.get("dev_name1"), params.get("dev_name2")
        autoModeCtrl.th_soil = int(config_data['soil'])


        if params.get('dev_time') is not None:
            time = params.get('dev_time')
            date = params.get('dev_date')
            year = int(date[0:4])
            month = int(date[5:7])
            day = int(date[8::])
            hour = int(time[0:2])
            minute = int(time[3:5])
            rtc.datetime((year, month, day, 0, hour, minute, 0, 0))
        else:
            date, time = getRtcTime()
            config_data['dev_time']=time
            config_data['dev_date']=f'{date[-4::]}-{date[3:5]}-{date[0:2]}' #convert to datetime notation yy-mm-dt
       
        with open ("config.json", "w+") as file:
            json.dump(config_data, file) 
     
        return send_file('config.json')
    
    else:
        
        return send_file('config.json')


@app.route('/control', methods=['GET', 'POST'])
async def control(request):
    
    params = request.args #request args from GET
    print("params from GET control", params)

    if 'wifi' in params: #fetch(`/config.json?wifi=${wifi_mode}&ssid=${params['ssid']}&ssid_pass=${params['ssid_pass']}`);
       
        with open('boot_ini.json', 'r') as input:
            settings = json.load(input)
         

        settings['DEFAULT_WIFI_MODE'] = params.get('wifi')
       

        if len(params.get('ssid')) > 0:
            settings['SSID'] = params.get('ssid')
        if len(params.get('ssid_pass')):
            settings['SSID_PWD'] = params.get('ssid_pass')
        

        with open('boot_ini.json', 'w') as input:
             json.dump(settings, input)
    
    if "auto_mode" not in params:
        #print("return no auto ")
        return Response(body="wrong parameters passed")
           


    if "ON" in params.get('auto_mode'):
       autoModeCtrl.status = True
    if "OFF"in params.get('auto_mode'):
        autoModeCtrl.status = False
       
    if params['device1'] == 'ON':
        device1.start()
    if params['device1'] == 'OFF':
       device1.stop()

    if params['device2'] == 'ON':
       device2.start()
    if params['device2'] == 'OFF':
       device2.stop()
           
    return Response(body=params, headers = {"Content-Security-Policy-Report-Only" : "default-src 'self'"}) 

@app.route('/log.txt')
async def log(request):
    return send_file('log.txt')

    
@app.route('/boot_ini.json')
async def log(request):
    return send_file('boot_ini.json')

@app.route('/javascript2.js')
async def log(request):
    return send_file('javascript2.js')


@app.route('/index2.html')
async def log(request):
    return send_file('index2.html')


@app.route('/favicon.ico')
async def favicon(request):
    return send_file('/static/favicon.ico')    


@app.route('/chart', methods=['GET', 'POST']) #send log with data for charts. Data prepared by "writeLog()"
async def chart(request):
    return send_file("log2.json")

@app.route('/log2.json')
async def log(request):
    return send_file('log2.json')

@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'



async def main():

    task1 = asyncio.create_task(app.start_server(port=80, debug=True))
    task2 = asyncio.create_task(writeLog())
    task3 = asyncio.create_task(deviceControl())
    task4 = asyncio.create_task(emergencyDeviceControl())
    await task1
    await task2
    await task3
    await task4
    
    
    
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()  # Clear retained state