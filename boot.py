# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import json
import webrepl
import network
from config import *

from esp8266_i2c_lcd import I2cLcd
from machine import Pin, SoftI2C as I2C
from time import sleep

DEFAULT_I2C_ADDR = 0x27 #addr for LCD


i2c = I2C(scl=Pin(22), sda=Pin(21), freq=100000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)
lcd.clear()
lcd.move_to(0, 0)



def do_connect():
    
    
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('connecting to network...')
        lcd.putstr("Connecting")
        wlan.active(True)
        wlan.connect(SSID, SSID_PWD)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    ip_addr = wlan.ifconfig()[0]
    lcd.putstr(f"IP: \n {wlan.ifconfig()[0]}")
    sleep(0.5)
    lcd.backlight_off()
    
    
with open ("log2.json", "w+") as f:
    json.dump(JSON_LOG_DATA, f)



do_connect()
print("Connected")

webrepl.start()
print("Web REPL started")





 

