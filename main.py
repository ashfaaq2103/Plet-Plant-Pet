import os
import cv2
import threading
import time
import speech_recognition as sr
import serial
from datetime import datetime, timedelta
from queue import Queue
import numpy as np
from sface import SFace
from yunet import YuNet
import sounddevice

# Define the serial port (USB port 0)
serial_port = '/dev/ttyUSB0'

serial_port2 = '/dev/ttyUSB1'

moisture_level_file_path = 'moisture_level.txt'

hours_of_light = 8 

current_plant_name = 'succulent'

baud_rate2 = 19200

# Define the baud rate (make sure it matches with your Arduino code)
baud_rate = 9600

# Initialize the recognizer
recognizer = sr.Recognizer()

# Flag to control video playback
video_lock = threading.Lock()
video_queue = Queue()
wait_time_human = 150

max_moisture_value = 1000

moisture_value = 100

faceRecognized = False 
humanDetected = False

ser2 = serial.Serial(serial_port2, baud_rate2)

# Create serial connection 1 
ser = serial.Serial(serial_port, baud_rate)


# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


# Create the OpenCV window
cv2.namedWindow('Video Player', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('Video Player',  cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
#cv2.setWindowProperty('Video Player',  cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

def check_plant_name():
    """
    Check the plant name from a file.
    If the file doesn't exist, set a default plant name.
    """
    default_plant_name = "succulent"
    while True:
        try:
            with open('plantName.txt', 'r') as file:
                plant_name = file.read().strip()
                return plant_name
        except FileNotFoundError:
            plant_name = default_plant_name
            return plant_name
            # Perform default actions for default plant name

def initialize_capture(camera_index=0):
    """
    Initialize video capture from the webcam.
    """
    # Open webcam video stream
    cap = cv2.VideoCapture(camera_index)
    return cap


def play_video(video_name, duration):
    """
    Play a video file for a specified duration.
    """
    video_path = os.path.join("Videos", video_name)
    if not os.path.exists(video_path):
        print(f"Video '{video_name}' not found.")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file '{video_name}'.")
        return

    start_time = time.time()
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Video Player', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
            if time.time() - start_time >= duration:
                break
        else:
            break

    cap.release()

def change_video(video_name):
    """
    Change the currently playing video.
    """
    global current_video
    with video_lock:
        current_video = video_name

def listen_for_trigger_phrase():
    """
    Listen for trigger phrases using speech recognition.
    """
    global humanDetected
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            trigger_detected = False
            while faceRecognized == True:  # Listen for same amount of time set for human detection
                audio_data = recognizer.listen(source)
                try:
                    # Recognize the trigger phrase
                    trigger_phrase = recognizer.recognize_google(audio_data)
                    if any(word in trigger_phrase.lower() for word in ["hello", "hi", "hey", "greetings"]):
                        user_input = "happy.mp4"
                        ser.write("hello".encode())
                        ser2.write("greet".encode())
                        video_queue.put(user_input)
                        trigger_detected = True
                    if any(word in trigger_phrase.lower() for word in ["run", "show", "play", "dance"]):
                        user_input = "run.mp4"
                        ser.write("run".encode())
                        ser2.write("play".encode())
                        video_queue.put(user_input)
                        trigger_detected = True
                    if any(word in trigger_phrase.lower() for word in ["bye", "Goodbye"]):
                        user_input = "bye.mp4"
                        ser.write("sad".encode())
                        video_queue.put(user_input)
                        trigger_detected = True
                    if any(word in trigger_phrase.lower() for word in ["how are you", "how are", "how you"]):
                        user_input = "dizzy.mp4"
                        ser.write("happy".encode())
                        video_queue.put(user_input)
                        trigger_detected = True
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Could not request results from service; {e}")
                    
                if trigger_detected:
                    time.sleep(0.3)  # Sleep briefly to avoid high CPU usage
                    continue
            #print("Time is up")
            
            
def check_water_level():
    """
    Check the water level and take actions accordingly.
    """
    global moisture_value
    global max_moisture_value
    if moisture_value > max_moisture_value:
        ser2.write("water".encode())
        ser.write("anger".encode())
        
                
def computerVision():
    """
    Perform computer vision tasks including human and face detection.
    """
    global humanDetected 
    global faceRecognized
    global wait_time_human
    human_detected_time = 0 
    cap = initialize_capture()
    while True:
        while humanDetected == False :
            
            # Capture frame-by-frame
            ret, frame = cap.read()

            # Resizing for faster detection
            frame = cv2.resize(frame, (640, 480))

            # Convert to grayscale for faster detection
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # Detect people in the image (without displaying)
            boxes, weights = hog.detectMultiScale(gray, winStride=(8, 8))
            
            # Check if any humans are detected
            if len(boxes) > 0:

                human_detected_time = time.time()
                humanDetected = True 
                cap.release() 
                check_water_level() 
                recognition_start_time = time.time()
                faceRecognized = recognize_user() 
                break  # Exit the loop if human is detected
                
            time.sleep(0.1)
                
        if humanDetected and (time.time() - human_detected_time >= wait_time_human): # wait for predefined minutes 
            humanDetected = False  # Reset humanDetected to False
            if faceRecognized == True:
                faceRecognized = False 
            cap = initialize_capture()
            
        # Start face recognition process if human is detected
        if humanDetected:
            while time.time() - recognition_start_time <= 15:  # Run face recognition for 15 seconds
                if faceRecognized:
                    break
                faceRecognized = recognize_user()
                time.sleep(0.2)


        time.sleep(0.2)

def recognize_user():
    """
    Recognize the user's face.
    """
    target_image_path = "/home/pi/Desktop/captured_img.jpg"

    # Check if the file exists
    if not os.path.exists(target_image_path):
        return  # Break from the function

    # Hardcoded default values for model and vis arguments
    model_path = "./models/face_recognition_sface_2021dec.onnx"
    user_detected = False  # Flag to check if user is detected

    backend_target_pairs = [
        [cv2.dnn.DNN_BACKEND_OPENCV, cv2.dnn.DNN_TARGET_CPU],
        [cv2.dnn.DNN_BACKEND_CUDA,   cv2.dnn.DNN_TARGET_CUDA],
        [cv2.dnn.DNN_BACKEND_CUDA,   cv2.dnn.DNN_TARGET_CUDA_FP16],
        [cv2.dnn.DNN_BACKEND_TIMVX,  cv2.dnn.DNN_TARGET_NPU],
        [cv2.dnn.DNN_BACKEND_CANN,   cv2.dnn.DNN_TARGET_NPU]
    ]

    backend_id = backend_target_pairs[0][0]  # Default backend ID
    target_id = backend_target_pairs[0][1]  # Default target ID

    # Instantiate SFace for face recognition
    recognizer = SFace(modelPath=model_path, disType=0, backendId=backend_id, targetId=target_id)

    # Instantiate YuNet for face detection
    detector = YuNet(modelPath='./models/face_detection_yunet_2023mar.onnx', inputSize=[320, 320],
                     confThreshold=0.9, nmsThreshold=0.3, topK=5000, backendId=backend_id, targetId=target_id)

    img1 = cv2.imread(target_image_path)

    start_time = time.time()
    while time.time() - start_time < 2:
        # Take a picture
        cap = initialize_capture()
        ret, query_img = cap.read()  # Capture a frame from the camera
        cap.release()  # Release the camera
        if ret:
            query_image = query_img  # Set the captured image as the query image
            
            # Detect faces in target and query images
            detector.setInputSize([img1.shape[1], img1.shape[0]])
            faces1 = detector.infer(img1)
            assert faces1.shape[0] > 0, 'Cannot find a face in the target image.'
            
            faces2 = detector.infer(query_image)
            if faces2.shape[0] == 0:
                continue

            # Match faces between target and query images
            scores = []
            matches = []
            for face in faces2:
                result = recognizer.match(img1, faces1[0][:-1], query_image, face[:-1])
                scores.append(result[0])
                matches.append(result[1])

            # Check if user is detected
            if True in matches:
                user_detected = True
                ser.write("hello".encode())
                ser2.write("greet".encode())
                break  # Stop capturing pictures if user is detected
            else:
                user_detected = False 

    return user_detected

def light_check():
    """
    Check the light level and adjust accordingly.
    """
    global hours_of_light
    global faceRecognized 

    start_time = datetime.now()
    while True:
        current_time = datetime.now()
        if start_time <= current_time - timedelta(hours=hours_of_light):
            ser2.write("nolight".encode())

        if start_time > current_time - timedelta(hours=hours_of_light):
            ser2.write("light".encode())

        if start_time <= current_time - timedelta(hours=24):
            start_time = datetime.now()
        time.sleep(5)
            
def setParametersPlant(plantName):
    """
    Set parameters for different types of plants.
    """
    global hours_of_light
    global max_moisture_value
    
    if plantName == "succulent":
        hours_of_light = 8; 
        max_moisture_value = 800
    if plantName == "flowers":
        hours_of_light = 7; 
        max_moisture_value = 600
    if plantName == "vege": 
        hours_of_light = 14; 
        max_moisture_value = 600
        

def main_prog():
    """
    Main program logic.
    """
    global humanDetected 
    global current_plant_name
    global hours_of_light
    global max_moisture_value
    
    # Start listening for trigger phrase in a separate thread
    listen_thread = threading.Thread(target=listen_for_trigger_phrase)
    listen_thread.daemon = True
    listen_thread.start()
    
    # Start serial input checking thread
    serial_thread = threading.Thread(target=check_serial_input)
    serial_thread.daemon = True
    serial_thread.start()

    # Start serial input checking thread
    serial_thread2 = threading.Thread(target=check_serial_input2)
    serial_thread2.daemon = True
    serial_thread2.start()


    # Start serial input checking thread
    light_thread = threading.Thread(target=light_check)
    light_thread.daemon = True
    light_thread.start()

    # Start serial input to check for human 
    computer_vision_thread = threading.Thread(target=computerVision)
    computer_vision_thread.daemon = True
    computer_vision_thread.start()

    # Start video playback
    while True:
        name_of_plant = check_plant_name()
        if current_plant_name != name_of_plant:
            setParametersPlant(name_of_plant)
        if humanDetected == True:
            current_video = "looking.mp4"
        else: 
            current_video = "sleep.mp4" 
            
        # Check if video queue has a video name
        if not video_queue.empty():
            video_name = video_queue.get()

            # Play video based on the name and duration
            if video_name == "happy.mp4":
                play_video(video_name, duration=3)
            elif video_name == "run.mp4":
                play_video(video_name, duration=7)
            elif video_name == "bye.mp4":
                play_video(video_name, duration=6)
            elif video_name == "Angry.mp4":
                play_video(video_name, duration=6)
            elif video_name == "dizzy.mp4":
                play_video(video_name, duration=4)
            else:
                play_video(video_name, duration=2)

            # Update the current video being played
            change_video(video_name)
        else:
            # Play default video ("looking.mp4") if the queue is empty
            if current_video == "sleep.mp4":
                play_video(current_video, duration=2)
            else:
                play_video(current_video, duration=2)
                

def check_serial_input():
    """
    Check serial input for moisture level.
    """
    global moisture_value 
    global moisture_level_file_path
    while True:
        # Read data from serial port
        data = ser.readline().decode('latin-1').strip()
        if data:
            # Split data based on comma
            data_parts = data.split(",")
            moisture_value = int(data_parts[0].split(":")[1]) 
            # Write moisture level to file
            with open(moisture_level_file_path, 'w') as file:
                file.write(str(moisture_value))
            time.sleep(30)  # Wait for 60 seconds before updating again
            
        
def check_serial_input2():
    """
    Check serial input for lifted status.
    """
    lifted_detected = False
    while True:
        being_lifted = False 
        data = ser2.readline().decode('latin-1').strip()
        
        if data:
            # Split data based on comma
            data_parts = data.split(",") 

            if len(data_parts) > 1 and data_parts[1] == "lifted" and not lifted_detected:
                ser.write("anger".encode())  # Send "anger" command
                video_queue.put("Angry.mp4") 
                lifted_detected = True
                time.sleep(5)  # Delay for 5 seconds
                being_lifted = True
            else:
                lifted_detected = False
            
            if being_lifted == True:
                time.sleep(2)
            time.sleep(0.1)  # Short delay to avoid overwhelming CPU
            print("entered")
            ser2.write("greet".encode())



def main():
    """
    Main entry point of the program.
    """
    main_prog()


if __name__ == "__main__":
    main()
