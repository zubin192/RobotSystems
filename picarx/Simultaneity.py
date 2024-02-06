import time
from time import sleep
try:
    from robot_hat import ADC
except ImportError:
    from sim_robot_hat import ADC
from picarx_improved import Picarx
import concurrent.futures

FORWARD_ANGLE = 0
LEFT_ANGLE = -45
RIGHT_ANGLE = 45

class Bus:
    def __init__(self):
        self.message = None

    def write(self, message):
        if message is not None:
            self.message = message

    def read(self):
        if self.message is not None:
            return self.message
        else:
            return None

class Grayscale_Module:
    def __init__(self):
        self.chn_0 = ADC('A0')
        self.chn_1 = ADC('A1')
        self.chn_2 = ADC('A2')

    def get_grayscale_data(self):
        adc_value_list = [self.chn_0.read(), self.chn_1.read(), self.chn_2.read()]
        return adc_value_list
    
    def sensor_function(self, sensor_values_bus, sensor_delay):
        while True:
            grayscale_data = self.get_grayscale_data()
            sensor_values_bus.write(grayscale_data)
            print(f"Sensor function put data on bus: {grayscale_data}")
            time.sleep(sensor_delay)

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
        
    
    def interpreter_function(self, sensor_values_bus, interpreter_bus, interpreter_delay):
        while True:
            grayscale_values = sensor_values_bus.read()
            if grayscale_values is not None:
                print(f"Interpreter function read data from bus: {grayscale_values}")
                status = self.get_status(grayscale_values)
                interpreter_bus.write(status)
                print(f"Interpreter function put status on bus: {status}")
            time.sleep(interpreter_delay)
                

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

    def controller_function(self, interpreter_bus, controller_delay):
        while True:
            status = interpreter_bus.read()
            if status is not None:
                print(f"Controller function read status from bus: {status}")
                grayscale_values = grayscale_module.get_grayscale_data()  
                self.run_controller(grayscale_values, status)
            time.sleep(controller_delay)


if __name__ == "__main__":
    sensor_values_bus = Bus()
    interpreter_bus = Bus()

    sensor_delay = 0.001
    interpreter_delay = 0.01
    controller_delay = 0.05

    px = Picarx()
    px_power = 60

    grayscale_module = Grayscale_Module()
    interp = Interp(px)
    controller = Controller(px, px_power)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        eSensor = executor.submit(grayscale_module.sensor_function, sensor_values_bus, sensor_delay)
        eInterpreter = executor.submit(interp.interpreter_function, sensor_values_bus, interpreter_bus, interpreter_delay)
        eController = executor.submit(controller.controller_function, interpreter_bus, controller_delay)
        eSensor.result()
        eInterpreter.result()
        eController.result()