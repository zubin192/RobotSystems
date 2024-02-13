import rossros as rr
import logging
import time
from time import sleep
try:
    from robot_hat import ADC
except ImportError:
    from sim_robot_hat import ADC
from picarx_improved import Picarx
try:
    from robot_hat import Pin, fileDB
    from robot_hat import Grayscale_Module
    from robot_hat.utils import reset_mcu
except ImportError:
    from sim_robot_hat import Pin, fileDB
    from sim_robot_hat import Grayscale_Module
import logging

px = Picarx()
logging.getLogger().setLevel(logging.INFO)

FORWARD_ANGLE = 0
LEFT_ANGLE = -45
RIGHT_ANGLE = 45
POWER = 25

class Sensing:
    def __init__(self):
        self.chn_0 = ADC('A0')
        self.chn_1 = ADC('A1')
        self.chn_2 = ADC('A2')

    def get_grayscale_data(self):
        adc_value_list = [self.chn_0.read(), self.chn_1.read(), self.chn_2.read()]
        return adc_value_list

class UltraSonic:
    def __init__(self, pax):
        self.car = pax

    def read(self):
        return self.car.get_distance()

class Interp:
    
    def __init__(self, pax, sensing):
        self.car = pax
        self.sensing = sensing
    def get_status(self, val_list):
        _state = self.car.get_line_status(val_list)
        print(_state)
        if _state == [0, 0, 0]:
            return 'stop'
        elif _state == [0, 1, 0]:
            return 'forward'
        elif _state == [0, 0, 1]:
            return 'right'
        elif _state == [1, 0, 0]:
            return 'left'


class Controller:
    def __init__(self, pax, power, sensing):
        self.car = pax
        self.power = power
        self.last_state = "stop"
        self.sensing = sensing

    def run_controller(self, grayscale_values, status):
        print("Grayscale Values:", grayscale_values)
        print("Status:", status)
        if grayscale_values != "stop":
            self.last_state = status
        
        if grayscale_values == 'forward':
            self.car.set_dir_servo_angle(FORWARD_ANGLE)
  
        elif grayscale_values == 'left':
            self.car.set_dir_servo_angle(LEFT_ANGLE)

        elif grayscale_values == 'right':
            self.car.set_dir_servo_angle(RIGHT_ANGLE)

        distance = status
        if distance < 10:
                self.car.stop()
        else:
            self.car.forward(30)
        
            
# Create Sensing, Interp, and Controller instances
sensing = Sensing()
Ultrasonic1 = UltraSonic(px)
interp = Interp(px, sensing)
controller = Controller(px, POWER, Ultrasonic1)

# Initiate data and termination busses
bSensing = rr.Bus(0,"Sensing Stuff")
bUltrasonicSensor = rr.Bus(0,"Ultrasonic Sensor Stuff")
bInterp = rr.Bus(0, "Interp Stuff")
bTerminate = rr.Bus(0, "Termination Bus")


readSensor = rr.Producer(
    sensing.get_grayscale_data,  # function that will generate data
    bSensing,  # output data bus
    0.01,  # delay between data generation cycles
    bTerminate,  # bus to watch for termination signal
    "Read sensor")

UltrasonicSensor1 = rr.Producer(
    Ultrasonic1.read,  # function that will generate data
    bUltrasonicSensor,  # output data bus
    0.01,  # delay between data generation cycles
    bTerminate,  # bus to watch for termination signal
    "Ultrasonic Sensor")

interp = rr.ConsumerProducer(
    interp.get_status,  # function that will consume data
    bSensing, #input data bus
    bInterp,  # output data bus
    0.1,  # delay between data consumption cycles
    bTerminate,  # bus to watch for termination signal
    "Interp")

controller = rr.Consumer(
    controller.run_controller,  # function that will consume data
    (bInterp,bUltrasonicSensor),  # input data bus
    0.5,  # delay between data consumption cycles
    bTerminate,  # bus to watch for termination signal
    "Controller")


# Make a printer that returns the most recent wave and product values
printBuses = rr.Printer(
    (bSensing, bInterp, bUltrasonicSensor),  # Buses to print
    0.5,  # Period
    "Print Buses")  # Name of this printer

# Make a timer that turns on the termination bus when it triggers
terminationTimer = rr.Timer(
    bTerminate,  # Output data bus
    20,  # Duration
    0.1,  # Delay between checking for termination time
    bTerminate,  # Bus to check for termination signal
    "Termination timer")  # Name of this timer

# Create a list of producers, consumers, printers, and timers to execute concurrently
producer_consumer_list = [readSensor,UltrasonicSensor1 ,interp,controller, printBuses, terminationTimer]

# Execute the list of producer-consumers concurrently
rr.runConcurrently(producer_consumer_list)
