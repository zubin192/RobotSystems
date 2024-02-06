import time
from time import sleep
try:
    from robot_hat import ADC
except ImportError:
    from sim_robot_hat import ADC
from picarx_improved import Picarx

px = Picarx()

px_power = 0
last_state = "stop"

class Grayscale_Module(object):
    def __init__(self):
        self.chn_0 = ADC('A0')
        self.chn_1 = ADC('A1')
        self.chn_2 = ADC('A2')

    def get_grayscale_data(self):
        adc_value_list = [self.chn_0.read(), self.chn_1.read(), self.chn_2.read()]
        return adc_value_list

class Interp(object):
    @staticmethod
    def get_status(val_list):
        _state = px.get_line_status(val_list)  # Assuming px is defined elsewhere
        if _state == [0, 0, 0]:
            return 'stop'
        elif _state == [0, 1, 0]:
            return 'forward'
        elif _state == [0, 0, 1]:
            return 'right'
        elif _state == [1, 0, 0]:
            return 'left'
            

class Controller(object):
    @staticmethod
    def get_position(val_list):
        # Calculate the average grayscale value
        avg_value = sum(val_list) / len(val_list)
        
        position = (avg_value - 127.5) / 127.5
        
        return position

    @staticmethod
    def run_controller():
        while True:
            gm_val_list = px.get_grayscale_data()
            gm_state = Interp.get_status(gm_val_list)  # Use Interp class for status
            print("outHandle gm_val_list: %s, %s" % (gm_val_list, gm_state))
            
            # Get the position based on the grayscale values
            position = Controller.get_position(gm_val_list)
            print("Position:", position)
            
            if gm_state != 'stop':
                # Set the last state based on the position
                last_state = position
                
                # Adjust the angle and direction based on the last state
                px.set_dir_servo_angle(last_state * 45)
                px.forward(px_power)
            
            sleep(0.001)

if __name__ == "__main__":
    # Create an instance of Grayscale_Module
    grayscale_sensor = Grayscale_Module()

    # Create an instance of Interp
    interp = Interp()

    # Continuously print grayscale values, status, and position
    try:
        while True:
            grayscale_values = grayscale_sensor.get_grayscale_data()
            status = interp.get_status(grayscale_values)
            print("Grayscale Values:", grayscale_values)
            print("Status:", status)

            if status != "stop":
                # Set the last state based on the position
                last_state = Controller.get_position(grayscale_values)

            if status == 'forward':
                px.set_dir_servo_angle(0)
                px.forward(px_power) 
            elif status == 'left':
                px.set_dir_servo_angle(last_state * -45)  # Adjust the angle and direction based on the last state
                px.forward(px_power) 
            elif status == 'right':
                px.set_dir_servo_angle(last_state * 45)  # Adjust the angle and direction based on the last state
                px.forward(px_power) 

            time.sleep(0.001)  # Adjust the sleep duration as needed
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        px.stop()
        print("stop and exit")
        sleep(0.1)
