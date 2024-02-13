#!/usr/bin/python3
"""
This file demonstrates the basic operation of a RossROS program.

First, it defines two signal-generator functions (a +/-1 square wave and a saw-tooth wave) and a
function for multiplying two scalar values together.

Second, it generates buses to hold the most-recently sampled values for the signal-generator functions,
the product of the two signals, and a countdown timer determining how long the program should run

Third, it wraps the signal-generator functions into RossROS Producer objects, and the multiplication
function into a RossROS Consumer-Producer object.

Fourth, it creates a RossROS Printer object to periodically display the current bus values, and a RossROS Timer
object to terminate the program after a fixed number of seconds

Fifth and finally, it makes a list of all of the RossROS objects and sends them to the runConcurrently function
for simultaneous execution

"""

import rossros as rr
import logging
import time
import math
import time
from time import sleep
try:
    from robot_hat import ADC
except ImportError:
    from sim_robot_hat import ADC
from picarx_improved import Picarx
import concurrent.futures

# logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

FORWARD_ANGLE = 0
LEFT_ANGLE = -45
RIGHT_ANGLE = 45

""" First Part: Signal generation and processing functions """

class Sensing:
    def __init__(self):
        self.chn_0 = ADC('A0')
        self.chn_1 = ADC('A1')
        self.chn_2 = ADC('A2')

    def get_grayscale_data(self):
        adc_value_list = [self.chn_0.read(), self.chn_1.read(), self.chn_2.read()]
        return adc_value_list
    
    def __init__(self, trig, echo, timeout=0.02):
        self.trig = trig
        self.echo = echo
        self.timeout = timeout

    def ultrasonic_sense(self):
        self.trig.low()
        time.sleep(0.01)
        self.trig.high()
        time.sleep(0.00001)
        self.trig.low()
        pulse_end = 0
        pulse_start = 0
        timeout_start = time.time()
        while self.echo.value() == 0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1
        while self.echo.value() == 1:
            pulse_end = time.time()
            if pulse_end - timeout_start > self.timeout:
                return -1
        during = pulse_end - pulse_start
        cm = round(during * 340 / 2 * 100, 2)
        return cm

    def read(self, times=10):
        for i in range(times):
            a = self.ultrasonic_sense()
            if a != -1:
                return a
        return -1
        

class Interp:
    def __init__(self, px):
        self.px = px

    def get_status(self, val_list):
        _state = self.px.get_line_status(val_list)
        if _state == [0, 0, 0]:
            return 'stop'
        elif _state == [0, 1, 0]:
            return 'forward'
        elif _state == [0, 0, 1]:
            return 'right'
        elif _state == [1, 0, 0]:
            return 'left'
        
    def ultrasonicstatus(self, distance, min_distance=10):
        if distance != -1 and distance < min_distance:
            return True
        return False
    
        
class Controller:
    def __init__(self, px, power, sensing):
        self.px = px
        self.power = power
        self.last_state = "stop"

    def get_position(self, val_list):
        avg_value = sum(val_list) / len(val_list)
        position = (avg_value - 127.5) / 127.5
        return position

    def run_controller(self, grayscale_values, status):
        print("Grayscale Values:", grayscale_values)
        print("Status:", status)

        if status != "stop":
            self.last_state = status

        if status == 'forward':
            self.px.set_dir_servo_angle(FORWARD_ANGLE)
            self.px.forward(self.power)
        elif status == 'left':
            self.px.set_dir_servo_angle(LEFT_ANGLE)
            self.px.forward(self.power)
        elif status == 'right':
            self.px.set_dir_servo_angle(RIGHT_ANGLE)
            self.px.forward(self.power)

        sleep(0.001)

    def stop_if_obstacle(self, min_distance=10):
        distance = self.sensing.read()
        if distance != -1 and distance < min_distance:
            self.px.stop()
            return True
        return False

    def run_controller(self, grayscale_values, status):
        print("Grayscale Values:", grayscale_values)
        print("Status:", status)

        if self.stop_if_obstacle():
            print("Obstacle detected, stopping.")
            return



""" Second Part: Create buses for passing data """

Sensing_stuff = Sensing()
Interp_stuff = Interp()
Controller_stuff = Controller()

# Initiate data and termination busses
bSensing = rr.Bus(Sensing_stuff, "Sensing Stuff")
bInterp = rr.Bus(Interp_stuff, "Interp Stuff")
bController = rr.Bus(Controller_stuff, "Controller Stuff")
bTerminate = rr.Bus(0, "Termination Bus")

""" Third Part: Wrap signal generation and processing functions into RossROS objects """

# Wrap signal generation and processing functions into RossROS objects
readGrayscale = rr.Producer(Sensing_stuff.get_grayscale_data, bSensing, "Read Grayscale")
getInterpStatus = rr.Producer(Interp_stuff.get_status, bSensing, bInterp, "Get Interp Status")
runController = rr.ConsumerProducer(Controller_stuff.run_controller, bSensing, bInterp, bController, "Run Controller")

""" Fourth Part: Create RossROS Printer and Timer objects """

# Make a printer that returns the most recent wave and product values
printBuses = rr.Printer(
    (bSquare, bSawtooth, bMultiplied, bTerminate),  # input data buses
    # bMultiplied,      # input data buses
    0.25,  # delay between printing cycles
    bTerminate,  # bus to watch for termination signal
    "Print raw and derived data",  # Name of printer
    "Data bus readings are: ")  # Prefix for output

# Make a timer (a special kind of producer) that turns on the termination
# bus when it triggers
terminationTimer = rr.Timer(
    bTerminate,  # Output data bus
    3,  # Duration
    0.01,  # Delay between checking for termination time
    bTerminate,  # Bus to check for termination signal
    "Termination timer")  # Name of this timer

""" Fifth Part: Concurrent execution """

# Create a list of producer-consumers to execute concurrently
producer_consumer_list = [readSquare,
                          readSawtooth,
                          multiplyWaves,
                          printBuses,
                          terminationTimer]

# Execute the list of producer-consumers concurrently
rr.runConcurrently(producer_consumer_list)
