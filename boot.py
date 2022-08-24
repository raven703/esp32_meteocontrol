# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import json
import time
import webrepl
import network
import urequests
from ssd1306 import SSD1306_I2C
from config import *


from machine import Pin, SoftI2C as I2C, RTC
rtc = RTC()




i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000) #setup I2C
display = SSD1306_I2C(128, 32, i2c) #init oled driver
display.fill(0)
display.text('Initializing...', 0, 0, 1) # text, x, y, pixel_state
display.show()

def setTime():
    url = "http://worldtimeapi.org/api/timezone/Europe/Moscow"
    
    try:
        response = urequests.get(url)
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
    except OSError:
        print("error in internet connection")
        print("Time is not set, using zero defaults")
        rtc.datetime((2022, 1, 1, 0, 1, 1, 1, 1))

def start_connect_point():
    
    
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('connecting to network...')
        
        wlan.active(True)
        wlan.connect(settings['SSID'], settings['SSID_PWD'])
        attemp = 0
        while not wlan.isconnected():
            attemp =+ 1
            print('trying to connect', attemp)
            if attemp >30:
                print("Can`t connect to WiFI")
                display.text('no carrier', 0, 12, 1) # text, x, y, pixel_state
                display.show()
                break
                
            pass

    print(wlan.ifconfig())
    display.text(str(wlan.ifconfig()), 0, 12, 1) # text, x, y, pixel_state
    display.show()
    return wlan.ifconfig()
    
 
    
def start_access_station():
   
    ap = network.WLAN(network.AP_IF) # create access-point interface
    ap.active(True)         # activate the interface
    ap.config(essid=settings['SSID'], authmode=3, password=settings['SSID_PWD']) # SSID of the access point, WPAPSK2
    ap.config(max_clients=10) # set how many clients can connect to the network
    ip_config = ap.ifconfig()
    print(ip_config)
    display.fill(0)
    
    display.text('mode: station', 0, 0, 1) # text, x, y, pixel_state
    
    display.text(f'ip:{ip_config[0]}', 0, 12, 1) # text, x, y, pixel_state
    display.show()
    return ap.ifconfig()



with open('boot_ini.json', 'r') as input:
    settings = json.load(input)

#check button for REST
buttonPin = Pin(13, Pin.IN, Pin.PULL_DOWN)


if buttonPin.value() == 1:
    print("Reset to station mode")
    settings['DEFAULT_WIFI_MODE'] = 'station'
    settings['SSID'] = 'GROW_ST2'
    settings['SSID_PWD'] = '12345678'
    display.fill(0)
    display.text('Reset detected', 0, 0, 1) # text, x, y, pixel_state
    display.text('station mode active', 0, 12, 1) # text, x, y, pixel_state
    display.show()
    with open('boot_ini.json', 'w') as input:
        json.dump(settings, input)
    time.sleep(2)


if settings['DEFAULT_WIFI_MODE'] == 'station':
    start_access_station()
    
elif settings['DEFAULT_WIFI_MODE'] == 'point':
    start_connect_point()
    display.text('mode: point', 0, 24, 1) # text, x, y, pixel_state
    display.show()







webrepl.start()
setTime()

