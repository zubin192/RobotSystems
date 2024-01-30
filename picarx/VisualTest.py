
import cv2
from picarx_improved import Picarx
import time

px = Picarx()

def process_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
        points = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            center = (x + w // 2, y + h // 2)
            points.append(center)
            cv2.circle(gray, center, 5, (255), -1)

        if len(points) == 2:
            return points, gray

    return None, gray

def control_robot(points, image_width):
    if points:
        point1, point2 = points
        deviation = (point1[0] + point2[0]) // 2 - image_width // 2
        print(f"Deviation: {deviation}")

        # Adjust the direction based on deviation
        px.set_dir_servo_angle(deviation)
        
        # Move forward
        px.forward(50)  # Adjust the forward power as needed

    return None

def main():
    px.set_cam_tilt_angle(-35)  # Set the initial tilt angle

    cap = cv2.VideoCapture(0)
    # Set desired frame width and height
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while True:
        ret, frame = cap.read()
        points, processed_image = process_image(frame)
        control_robot(points, frame.shape[1])

        cv2.imshow('Line Following', processed_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.001)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

