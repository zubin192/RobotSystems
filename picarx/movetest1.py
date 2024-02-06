from picarx_improved import Picarx
import time

if __name__ == "__main__":
   
        px = Picarx()
        
        
        direction = input("Enter 'F' for Forward or 'B' for Backward or 'LP' for Left Parallel or 'RP' for Right Parallel or 'KT' for K-Turn: ").upper()

        
        if direction == 'F':
            
            speed = float(input("Enter the speed for Forward: "))
            duration = float(input("Enter the duration in seconds: "))
            steering_angle = int(input("Enter the steering angle: "))

            px.set_dir_servo_angle(steering_angle)
            px.forward(speed)
            time.sleep(duration)
            px.stop()
            

        elif direction == 'B':
           
            speed = float(input("Enter the speed for Backward: "))
            duration = float(input("Enter the duration in seconds: "))
            steering_angle = int(input("Enter the steering angle: "))
            
            px.set_dir_servo_angle(steering_angle)
            px.backward(speed)
            time.sleep(duration)
            px.stop()
        

        elif direction == 'RP':
            px.set_dir_servo_angle(15)
            px.backward(60)
            time.sleep(0.75)
            px.set_dir_servo_angle(-15)
            px.backward(60)
            time.sleep(0.75)
            px.forward(50)
            px.set_dir_servo_angle(0)
            time.sleep(1)
            px.stop()

        elif direction == 'LP':
            px.set_dir_servo_angle(-15)
            px.backward(60)
            time.sleep(0.75)
            px.set_dir_servo_angle(15)
            px.backward(60)
            time.sleep(0.75)
            px.forward(50)
            px.set_dir_servo_angle(0)
            time.sleep(1)
            time.sleep(1)
            px.stop()

        elif direction == 'KT':
            px.set_dir_servo_angle(-15)
            px.forward(60)
            time.sleep(1)
            px.set_dir_servo_angle(15)
            px.backward(60)
            time.sleep(1)
            px.set_dir_servo_angle(-15)
            px.forward(60)
            time.sleep(1.5)
            px.forward(60)
            px.set_dir_servo_angle(0)
            time.sleep(1)
            px.stop()


            

        else:
            print("Invalid direction. Please enter 'F' or 'B'. Exiting.")
            exit()



   