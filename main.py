import uasyncio as asyncio
import urequests

from microdot_asyncio import Microdot, redirect, send_file, Response
from machine import Pin, SoftI2C as I2C, RTC
from htu21d import *
from esp8266_i2c_lcd import I2cLcd
from device import *

rtc = RTC()
autoWork = True

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
         date_str = "Date: {2:02d}.{1:02d}.{0:4d}".format(*rtc.datetime())
         time_str = "Time: {4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime())
         print(date_str)
         print(time_str)
         return True
         
    else:
        print("Time is not set")
        return False 

def getRtcTime():
    date_str = "Date: {2:02d}.{1:02d}.{0:4d}".format(*rtc.datetime())
    time_str = "Time: {4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime())
    return [date_str, time_str]
        
        
# setup webserver
app = Microdot()
setTime()

# 
gy21 = HTU21D(22,21)  #take temp and hum from sensor
fan = motorDevice(12)
pump = motorDevice(14)
print("FAN is: ", fan.status())
print("PUMP is: ", pump.status())

pumpControlPin = Pin(14,Pin.OUT)
soilMeter = Pin(13,Pin.IN)
fanControlPin = Pin(12,Pin.OUT)

pumpControlPin.off()
fanControlPin.off()


async def writeLog():
    
    while True: 
        
        for pos in range(25):
            f = open("log.json", "r+")
            f.seek(pos*6)
            temper = str(round(gy21.temperature))
            hum = str(round(gy21.humidity))
            #print (f.tell(), "pos=", pos)
            #print(f"Temp: {temper} RH: {hum}")       
            f.write(temper + "," + hum + ",")
            f.close()
            await asyncio.sleep(3000)

async def deviceControl():
    write_request = True
    last_max_temper = 0
    while True: 
        
        temper = round(gy21.temperature,1)
        hum = round(gy21.humidity,1)
        if temper < 30: last_max_temper = 30
        if autoWork and temper > 30:
          
            if temper > last_max_temper:
                last_max_temper = temper
                write_request = True
            
            if not fan.status()[0]: fan.start()
            if write_request:
                with open("log.txt", "a+") as output:
                    output.write(f'Temp: {temper} {getRtcTime()} \n')
                   
                    if round(gy21.temperature,1) > last_max_temper: 
                        write_request = True
                       
                    else:
                        write_request = False
                      
        else:
            if fan.status()[0]: fan.stop()
            
            write_request = True
        
        await asyncio.sleep(5)
    
@app.route('/')
async def hello(response):
    return send_file("sensors2.html")

@app.route('/data', methods=['GET', 'POST'])
async def data(request):
    temper = str(round(gy21.temperature, 1))
    hum = str(round(gy21.humidity,1))
    return Response(body=[temper, hum, 0, 0], headers = {"Content-Security-Policy-Report-Only" : "script-src 'unsafe-inline'"}) # t, h, LED, Fan

@app.route('/chart', methods=['GET', 'POST'])
async def chart(request):
    
    with open("log.json", "r") as f:
        result = [i for i in f.readline().strip().split(",") if len(i) > 0]
                
    return Response(body=result, headers = {"Content-Security-Policy-Report-Only" : "script-src 'unsafe-inline'"})
   
    

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
        return Response(body=[pump_state, fan_state, 0, 0], headers = {"Content-Security-Policy-Report-Only" : "default-src 'self'"}) #

    pump_button, fan_button = params.get('pump_status'), params.get('fan_status')
        
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

@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'



async def main():
    task1 = asyncio.create_task(app.start_server(port=80, debug=False))
    task2 = asyncio.create_task(writeLog())
    task3 = asyncio.create_task(deviceControl())
    await task1
    await task2
    await task3
    
asyncio.run(main())
