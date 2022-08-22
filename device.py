import time

from machine import Pin, Timer

def get_free_space():
    import uos, esp
    blksize = uos.statvfs('/')[0]
    fbs = uos.statvfs('/')[3]
    print ("Avilable storage is:",(blksize*fbs)/1024, "KB", "out of:", esp.flash_size()/1024,"KB",sep=" ")

class Button:
    pressed = False
    screen = 0
    

    def __init__(self, pin, callback, trigger = Pin.IRQ_RISING):
        pin.irq(trigger=trigger, handler = self.button_handler)
        self.callback = callback
        self.timer1 = Timer(1)
        self.pin = pin

    def call_callback(self, pin):       
        self.callback()


    def button_handler(self, pin):
        self.timer1.init(mode=Timer.ONE_SHOT, period=300, callback=self.call_callback)

    def value(self):
        return self.pin.value()
        
                


class autoModeControl(): #class for control Auto Mode
    status = False
    button_last_time = 0
    display_last_time = 0
    soilData = 0
    tempData = 0
    humData = 0
    th_humid_low = 0
    th_humid_high = 0
    th_soil = 0

    def autoStatus(self):        
        return self.auto




class motorDevice():
    isTimerSet = False
    startTime = 0
    periodStartTime = 0
    
    def __init__(self, pin_number, name) -> None:

        self.pinControl = Pin(pin_number,Pin.OUT) #set pin for control
        self.pinNumber = pin_number
        self.pinControl.off()
        self.name = name
        self.periodStartTime = time.time()
        
        pass

    def start(self):
        #print("start in pin = ", self.pinNumber)
        self.startTime = time.time()
        self.pinControl.on()
        if self.pinControl.value() == 1:
            return True
        else:
            return False
        
    def stop(self):
        #print("stop in pin = ", self.pinNumber)
        self.pinControl.off()
        if self.pinControl.value() == 0:
            return True
        else:
            return False
    
    def status(self):
        if self.pinControl.value() == 1:
            return [True, "Running"]
        else:
            return [False, "Stopped"]
    
    def running(self):
        if self.pinControl.value() == 1:
            return True
        else:
            return False


    
    def value(self):
        return self.pinControl.value()

        
