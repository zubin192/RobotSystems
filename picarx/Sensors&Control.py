import time

try:
    from robot_hat import ADC
except ImportError:
    from sim_robot_hat import ADC

class Sensor(object):

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

    grayscale_sensor = Sensor()

    try:
        while True:
            grayscale_values = grayscale_sensor.get_grayscale_data()
            print("Grayscale Values:", grayscale_values)
            time.sleep(0.1)  
    except KeyboardInterrupt:
        print("Program terminated by user.")
