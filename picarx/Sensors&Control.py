import time

try:
    from robot_hat import ADC
except ImportError:
    from sim_robot_hat import ADC

class Grayscale_Module(object):

    def __init__(self):
        self.chn_0 = ADC('A0')
        self.chn_1 = ADC('A1')
        self.chn_2 = ADC('A2')

    def get_grayscale_data(self):
        adc_value_list = []
        adc_value_list.append(self.chn_0.read())
        adc_value_list.append(self.chn_1.read())
        adc_value_list.append(self.chn_2.read())
        return adc_value_list

class Interp(object):
    def __init__(self, sensitivity=10, polarity='dark'):
        self.sensor = Grayscale_Module()  # Fix the class name here
        self.sensitivity = sensitivity
        self.polarity = polarity

    def get_status(self):
        grayscale_values = self.sensor.get_grayscale_data()
        _state = self.get_line_status(grayscale_values)  # Assuming get_line_status is defined in Interp
        if _state == [0, 0, 0]:
            return 'stop'
        elif _state[1] == 1:
            return 'forward'
        elif _state[0] == 1:
            return 'right'
        elif _state[2] == 1:
            return 'left'

    def get_line_status(self, grayscale_values):
        # Implement your logic to determine line status based on grayscale values
        # This is a placeholder, replace it with your actual implementation
        return [1, 0, 0]

if __name__ == "__main__":
    interp = Interp()

    try:
        while True:
            status = interp.get_status()
            print("Robot Status:", status)
            time.sleep(0.1)  
    except KeyboardInterrupt:
        print("Program terminated by user.")
