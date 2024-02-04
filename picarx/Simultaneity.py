import time
import concurrent.futures
from time import sleep
try:
    from robot_hat import ADC
except ImportError:
    from sim_robot_hat import ADC
from picarx_improved import Picarx
from readerwriterlock import rwlock



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
        # other initialization

    def get_grayscale_data(self):
        # retrieve grayscale data
        grayscale_data = [1, 2, 3]  # replace with actual data
        self.sensor_bus.write(grayscale_data)

class Interp(object):
    @staticmethod
    def get_status(val_list):
        # Your existing implementation

class Controller(object):
    @staticmethod
    def get_position(val_list):
        # Your existing implementation

    @staticmethod
    def run_controller(interpreter_bus, control_bus):
        while True:
            # Read data from the buses
            gm_val_list = interpreter_bus.read()

            # Your existing code for interpretation

            # Write control information to the control bus
            control_bus.write(control_data)

            time.sleep(0.001)

def sensor_function(sensor_bus, sensor_delay):
    grayscale_sensor = Grayscale_Module(sensor_bus)
    while True:
        grayscale_sensor.get_grayscale_data()
        time.sleep(sensor_delay)

def interpreter_function(sensor_bus, interpreter_bus, interpreter_delay):
    while True:
        grayscale_data = sensor_bus.read()
        status = Interp.get_status(grayscale_data)
        interpreter_bus.write(status)
        time.sleep(interpreter_delay)

def control_function(interpreter_bus, control_bus, control_delay):
    while True:
        status = interpreter_bus.read()
        # Your existing code for control
        time.sleep(control_delay)

if __name__ == "__main__":
    # Create instances of MessageBus
    sensor_bus = MessageBus()
    interpreter_bus = MessageBus()
    control_bus = MessageBus()

    # Create ThreadPoolExecutor for concurrent execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        eSensor = executor.submit(sensor_function, sensor_bus, sensor_delay=0.001)
        eInterpreter = executor.submit(interpreter_function, sensor_bus, interpreter_bus, interpreter_delay=0.001)
        eController = executor.submit(control_function, interpreter_bus, control_bus, control_delay=0.001)

        try:
            # Your existing code for setting up Picarx
            while True:
                time.sleep(1)  # Adjust sleep duration as needed
        except KeyboardInterrupt:
            print("Program terminated by user.")
        finally:
            # Your existing cleanup code
