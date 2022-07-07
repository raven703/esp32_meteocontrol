from machine import Pin


class motorDevice():
    def __init__(self, pin_number) -> None:

        self.pinControl = Pin(pin_number,Pin.OUT) #set pin for control
        self.pinNumber = pin_number
        self.pinControl.off()
        pass

    def start(self):
        #print("start in pin = ", self.pinNumber)
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

        


