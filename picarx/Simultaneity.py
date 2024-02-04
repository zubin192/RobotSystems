import time
import concurrent.futures
from time import sleep
try:
    from robot_hat import ADC
except ImportError:
    from sim_robot_hat import ADC
from picarx_improved import Picarx
from readerwriterlock import rwlock

import concurrent.futures
from readerwriterlock import rwlock
import time

class MessageBus(object):
    def __init__(self):
        self.message = None
        self.lock = rwlock.RWLockWriteD()

    def write(self, message):
        with self.lock.gen_wlock():
            self.message = message

    def read(self):
        with self.lock.gen_rlock():
            return self.message

class Grayscale_Module(object):
    def __init__(self, sensor_bus):
        self.sensor_bus = sensor_bus

    def get_grayscale_data(self):
        adc_value_list = [1, 2, 3]  # replace with actual data
        self.sensor_bus.write(adc_value_list)

class Interp(object):
    @staticmethod
    def get_status(val_list):
        if val_list == [0, 0, 0]:
            return 'stop'
        elif val_list == [0, 1, 0]:
            return 'forward'
        elif val_list == [0, 0, 1]:
            return 'right'
        elif val_list == [1, 0, 0]:
            return 'left'

class Controller(object):
    @staticmethod
    def get_position(val_list):
        avg_value = sum(val_list) / len(val_list)
        position = (avg_value - 127.5) / 127.5
        return position

    @staticmethod
    def run_controller(interpreter_bus, control_bus):
        last_state = "stop"
        px_power = 60
        px = Picarx()  # Assuming you have a Picarx class

        while True:
            gm_val_list = interpreter_bus.read()
            gm_state = Interp.get_status(gm_val_list)

            position = Controller.get_position(gm_val_list)

            if gm_state != 'stop':
                last_state = position

                # Adjust the angle and direction based on the last state
                px.set_dir_servo_angle(last_state * 45)
                px.forward(px_power)

            time.sleep(0.001)

if __name__ == "__main__":
    # Create instances of MessageBus
    sensor_bus = MessageBus()
    interpreter_bus = MessageBus()
    control_bus = MessageBus()

    # Create ThreadPoolExecutor for concurrent execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        eSensor = executor.submit(Grayscale_Module, sensor_bus, sensor_delay=0.001)
        eInterpreter = executor.submit(Interp, sensor_bus, interpreter_bus, interpreter_delay=0.001)
        eController = executor.submit(Controller, interpreter_bus, control_bus, control_delay=0.001)

        try:
            # Your existing code for setting up Picarx
            while True:
                time.sleep(1)  # Adjust sleep duration as needed
        except KeyboardInterrupt:
            print("Program terminated by user.")
        finally:
            # Your existing cleanup code
            pass  # Add cleanup code if needed
