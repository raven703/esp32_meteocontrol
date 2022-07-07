import uasyncio as asyncio
import urequests
import json

from microdot_asyncio import Microdot, redirect, send_file, Response
from machine import Pin, RTC, ADC
from htu21d import *
from device import *
FAN_TIME_COUNTER = 25 #1s * 2

rtc = RTC()


def setTime():
    url = "http://worldtimeapi.org/api/timezone/Europe/Moscow"
    response = urequests.get(url)
    if response.status_code == 200:
         datetime_str = str(response.json()["datetime"])
         year = int(datetime_str[0:4])
         month = int(datetime_str[5:7])
         day = int(datetime_str[8:10])
         hour = int(datetime_str[11:13])
         minute = int(datetime_str[14:16])
         second = int(datetime_str[17:19])
         subsecond = int(round(int(datetime_str[20:26]) / 10000))

         rtc.datetime((year, month, day, 0, hour, minute, second, subsecond))
         #date_str = "Date: {2:02d}.{1:02d}.{0:4d}".format(*rtc.datetime())
         #time_str = "Time: {4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime())
         return True
         
    else:
        print("Time is not set")
        return False 

def getRtcTime():
    date_str = "{2:02d}.{1:02d}.{0:4d}".format(*rtc.datetime())
    time_str = "{4:02d}:{5:02d}".format(*rtc.datetime())
    return [date_str, time_str]
        
        
# setup webserver
app = Microdot()
setTime()

# 
gy21 = HTU21D(22,21)  #take temp and hum from sensor
fan = motorDevice(12)
pump = motorDevice(14)


pumpControlPin = Pin(14,Pin.OUT)
fanControlPin = Pin(12,Pin.OUT)
soilMeter = ADC(Pin(34), atten=ADC.ATTN_11DB)

pumpControlPin.off()
fanControlPin.off()


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
            
        temper = round(gy21.temperature)
        hum = round(gy21.humidity)
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

        with open ("log2.json", "r+") as f:
            json.dump(data, f)
          
        await asyncio.sleep(3200)


async def emergencyFanOFF(): #counter for emerg shutdown fan or pump in seconds.
    counter = 0
    while True:
        
        while fan.status()[0]: #fan is on, start count 5 min then turn it off
            counter += 1
            await asyncio.sleep(2) 
            #print("fan running time: ", counter*2)
            if not fan.status()[0]:
                counter = 0
                break
            if counter == FAN_TIME_COUNTER: #counter for emerg shutdown fan or pump in seconds.
                fan.stop()
                counter = 0
        await asyncio.sleep(1) 


async def emergencyPumpOFF(): #counter for emerg shutdown fan or pump in seconds.
    counter = 0
    while True:
        
        while pump.status()[0]: #pump is on, start count 5 min then turn it off
            counter += 1
            await asyncio.sleep(2) 
            #print("pump running time: ", counter*2)
            if not pump.status()[0]:
                counter = 0
                break
            if counter == FAN_TIME_COUNTER: #counter for emerg shutdown fan or pump in seconds.
                pump.stop()
                counter = 0
        await asyncio.sleep(1) 
            
     

async def deviceControl(): #control for pump and fan. Can use auto control or manual
    
    write_request = True
    last_max_temper = 0
    with open("control.txt", "r") as input:   
        state = input.read()
    autoMode = state
    
    while True: 
        
        temper = round(gy21.temperature,1)
        hum = round(gy21.humidity,1)
        if temper < 30:
            last_max_temper = 0
        
        with open ("log2.json", "r") as f:
                data = json.load(f)
        soil_data_len = len([i for i in data["soil"] if i>0])
        if soil_data_len > 0:
            soilData = int(sum(data["soil"][:-4:-1]) / len(data["soil"][:-4:-1]))
        
                

        with open("control.txt", "r") as input:   
            state = input.read()
           
        if state == "ON": autoMode = True
        if state == "OFF": autoMode = False
    
        if autoMode:
            print("auto mode ON")
            if temper > 30:
                if temper > last_max_temper:
                    last_max_temper = temper
                    write_request = True
                if not fan.status()[0]:
                    fan.start()
            
                if write_request:
                    with open("log.txt", "a+") as output:
                        output.write(f'Temp: {temper} {getRtcTime()} \n')
                    if round(gy21.temperature,1) > last_max_temper: 
                        write_request = True
                    else:
                        write_request = False
            if temper <30 :
                fan.stop()
                write_request = True
            
            
            if soilData > 190:
                print(soilData, "ALERT NEED WATER !!!!")

            else:
            #if fan.status()[0]:
            #    fan.stop()
                write_request = True
        
        await asyncio.sleep(5)
    
@app.route('/')
async def index(response):
    return send_file("sensors2.html")

@app.route('/data', methods=['GET', 'POST'])
async def data(request):
    await asyncio.sleep(1)
    with open("control.txt", "r") as input:   
        state = input.read()
    autoMode = state

    temper = round(gy21.temperature, 1)
    hum = round(gy21.humidity,1)
    soil = soilMeter.read()/10
    return Response(body=[temper, hum, soil, autoMode], headers = {"Content-Security-Policy-Report-Only" : "script-src 'unsafe-inline'"}) # t, h, LED, Fan

@app.route('/chart', methods=['GET', 'POST']) #send log with data for charts. Data prepared by "writeLog()"
async def chart(request):
    return send_file("log2.json")
   
    

@app.route('/control', methods=['GET', 'POST'])
async def control(request):
    pump_state = ""
    fan_state = ""
    params = request.args #requesr args from GET
   
    if pumpControlPin.value() == 0: 
        pump_state = "OFF"
    else:
        pump_state = "ON"

    if fanControlPin.value() == 0: 
        fan_state = "OFF"
    else:
        fan_state = "ON"

    if len(params) == 0:
        with open("control.txt", "r") as input:   
            autoMode = input.read()
        return Response(body=[pump_state, fan_state, autoMode, 0], headers = {"Content-Security-Policy-Report-Only" : "default-src 'self'"}) #

    pump_button, fan_button, auto_mode  = params.get('pump_status'), params.get('fan_status'), params.get('auto_mode')
    print("PARAMS AUTO", params.get('auto_mode'))
    
    if auto_mode == "ON": 
        with open("control.txt", "w+") as output:
            output.write("ON")

    else:
        with open("control.txt", "w+") as output:
            output.write("OFF")
            
    if pump_button == "1":
        if pumpControlPin.value() == 0:
            pumpControlPin.value(1)
            pump_state = "ON"
            return Response(body=[pump_state, fan_state, 0, 0], headers = {"Content-Security-Policy-Report-Only" : "default-src 'self'"}) #
        else:
            pumpControlPin.value(0)
            pump_state = "OFF"
            return Response(body=[pump_state, fan_state, 0, 0], headers = {"Content-Security-Policy-Report-Only" : "default-src 'self'"}) #
    elif fan_button == "1":
        if fanControlPin.value() == 0:
            fanControlPin.value(1)
            fan_state = "ON"
            return Response(body=[pump_state, fan_state, 0, 0], headers = {"Content-Security-Policy-Report-Only" : "default-src 'self'"}) #
        else:
            fanControlPin.value(0)
            fan_state = "OFF"
            return Response(body=[pump_state, fan_state, 0, 0], headers = {"Content-Security-Policy-Report-Only" : "default-src 'self'"}) #

   

@app.route('/javascript.js')
async def javascript(response):
    return send_file('javascript.js')

@app.route('/gauge.min.js')
async def gauge(response):
    return send_file('gauge.min.js')

@app.route('/log.txt')
async def log(request):
    return send_file('log.txt')

@app.route('/log2.json')
async def log(request):
    return send_file('log2.json')

@app.route('/favicon.ico')
async def favicon(request):
    return send_file('favicon.ico')    

@app.route('/local.css')
async def local_css(request):
    return send_file('local.css')  


@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'



async def main():
    task1 = asyncio.create_task(app.start_server(port=80, debug=False))
    task2 = asyncio.create_task(writeLog())
    task3 = asyncio.create_task(deviceControl())
    task4 = asyncio.create_task(emergencyFanOFF())
    #task5 = asyncio.create_task(emergencyPumpOFF())
    await task1
    await task2
    await task3
    await task4
    #await task5
    
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()  # Clear retained state