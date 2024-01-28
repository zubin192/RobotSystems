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

if __name__ == "__main__":
    # Create an instance of Grayscale_Module
    grayscale_sensor = Grayscale_Module()

    # Continuously print grayscale values
    try:
        while True:
            grayscale_values = grayscale_sensor.get_grayscale_data()
            print("Grayscale Values:", grayscale_values)
            time.sleep(1)  # Adjust the sleep duration as needed
    except KeyboardInterrupt:
        print("Program terminated by user.")
