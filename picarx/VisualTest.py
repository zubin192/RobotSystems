import cv2
import numpy as np
from picarx_improved import Picarx
import time

px = Picarx()

def process_image(image):
    # Convert the image to the HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the lower and upper HSV thresholds for the color of the tape
    lower_color = np.array([20, 100, 100])
    upper_color = np.array([30, 255, 255])

    # Create a binary mask using the inRange function
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Apply Gaussian blur to the binary mask
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)

    # Apply morphological operations (erosion and dilation)
    kernel = np.ones((5, 5), np.uint8)
    morphed = cv2.morphologyEx(blurred, cv2.MORPH_OPEN, kernel)

    # Find contours in the processed mask
    contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Filter contours based on area (remove small contours)
        contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]

        # Ignore contours in the top 1/3 of the frame
        height, _ = image.shape[:2]
        threshold_y = height // 3
        contours = [cnt for cnt in contours if np.mean(cnt[:, :, 1]) > threshold_y]

        # Sort contours based on their x-coordinate to separate left and right contours
        contours = sorted(contours, key=lambda c: cv2.minEnclosingCircle(c)[0][0])

        # Draw contours on the original image
        cv2.drawContours(image, contours, -1, (0, 255, 0), 2)

        return contours, image

    return None, image

def calculate_deviation(contours, image_width):
    if contours is not None and len(contours) >= 2:
        # Calculate the midpoint of the two outermost contours
        midpoint1 = np.mean(contours[0], axis=0, dtype=int)
        midpoint2 = np.mean(contours[-1], axis=0, dtype=int)

        # Calculate the average midpoint
        average_midpoint = (midpoint1 + midpoint2) // 2

        # Calculate the deviation from the center of the image
        deviation = average_midpoint[0, 0] - image_width / 2

        # Adjust the scaling factor based on your needs
        scaling_factor = 0.2  # Increase or decrease as needed
        scaled_deviation = deviation * scaling_factor

        return scaled_deviation

    return None

def control_robot(contours, image_width):
    if contours is not None and len(contours) >= 2:
        deviation = calculate_deviation(contours, image_width)

        # Handle the case where deviation is None
        deviation = deviation if deviation is not None else 0

        print(f"Deviation: {deviation}")

        # Smooth the deviation to prevent abrupt changes
        smoothed_deviation = 0.9 * deviation

        # Adjust the direction based on smoothed deviation
        px.set_dir_servo_angle(smoothed_deviation)

        # Move forward with a non-zero value
        px.forward(70)  # Adjust the forward power as needed

    return None

def main():
    px.set_cam_tilt_angle(-40)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        tape_contours, processed_image = process_image(frame)
        control_robot(tape_contours, frame.shape[1])

        cv2.imshow('Processed Image', processed_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.01)  # Adjust the sleep duration

    cap.release()
    cv2.destroyAllWindows()
    time.sleep(0.01)


if __name__ == "__main__":
    main()
