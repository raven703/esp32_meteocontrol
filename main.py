import uasyncio as asyncio
from microdot_asyncio import Microdot, redirect, send_file, Response
from machine import Pin, SoftI2C as I2C
from htu21d import *
from esp8266_i2c_lcd import I2cLcd


# setup webserver
app = Microdot()
# 
gy21 = HTU21D(22,21)  #take temp and hum from sensor

pumpControlPin = Pin(14,Pin.OUT)
fanControlPin = Pin(12,Pin.OUT)

pumpControlPin.off()
fanControlPin.off()


async def printTemper():
    
    while True: 
        
        for pos in range(25):
            f = open("log.json", "r+")
            f.seek(pos*6)
            temper = str(round(gy21.temperature))
            hum = str(round(gy21.humidity))
            #print (f.tell(), "pos=", pos)
            f.write(temper + "," + hum + ",")
            print(f"Temp: {temper} RH: {hum}")
            f.close()
            await asyncio.sleep(3000)
    
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
    task2 = asyncio.create_task(printTemper())
    await task1
    await task2
    
asyncio.run(main())
