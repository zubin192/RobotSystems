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
from time import sleep
try:
    from robot_hat import ADC
except ImportError:
    from sim_robot_hat import ADC
from picarx_improved import Picarx
import rossros as rr
import logging
import time
import math

FORWARD_ANGLE = 0
LEFT_ANGLE = -45
RIGHT_ANGLE = 45
POWER = 0
stop_distance = 20

# logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)


""" First Part: Signal generation and processing functions """

class Grayscale_Module:
    def __init__(self):
        self.chn_0 = ADC('A0')
        self.chn_1 = ADC('A1')
        self.chn_2 = ADC('A2')

    def get_grayscale_data(self):
        adc_value_list = [self.chn_0.read(), self.chn_1.read(), self.chn_2.read()]
        return adc_value_list
    
class Ultrasonic_Module:

    def main():
        try:
            px = Picarx()
            # px = Picarx(ultrasonic_pins=['D2','D3']) # tring, echo
        
            while True:
                distance = round(px.ultrasonic.read(), 2)
                print("distance: ", distance)
                if distance > stop_distance:
                    px.forward(POWER)
                else:
                    px.forward(0)  # Stop the car

        finally:
            px.forward(0)

        
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
        
    
                
class Controller:
    def __init__(self, px, power):
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

  

""" Second Part: Create buses for passing data """

# Initiate data and termination busses
bSquare = rr.Bus(square(), "Square wave bus")
bSawtooth = rr.Bus(sawtooth(), "Sawtooth wave Bus")
bMultiplied = rr.Bus(sawtooth() * square(), "Multiplied wave bus")
bTerminate = rr.Bus(0, "Termination Bus")

""" Third Part: Wrap signal generation and processing functions into RossROS objects """

# Wrap the square wave signal generator into a producer
readSquare = rr.Producer(
    square,  # function that will generate data
    bSquare,  # output data bus
    0.05,  # delay between data generation cycles
    bTerminate,  # bus to watch for termination signal
    "Read square wave signal")

# Wrap the sawtooth wave signal generator into a producer
readSawtooth = rr.Producer(
    sawtooth,  # function that will generate data
    bSawtooth,  # output data bus
    0.05,  # delay between data generation cycles
    bTerminate,  # bus to watch for termination signal
    "Read sawtooth wave signal")

# Wrap the multiplier function into a consumer-producer
multiplyWaves = rr.ConsumerProducer(
    mult,  # function that will process data
    (bSquare, bSawtooth),  # input data buses
    bMultiplied,  # output data bus
    0.05,  # delay between data control cycles
    bTerminate,  # bus to watch for termination signal
    "Multiply Waves")

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
