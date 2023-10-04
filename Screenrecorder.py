import cv2
import numpy as np
import pyautogui
import threading

# Screen dimensions (adjust these based on your screen resolution)
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Video parameters
FPS = 30
OUTPUT_FILENAME = "screen_recording.mp4"

# Flag to stop recording
recording = True

# Function to record the screen
def record_screen():
    global recording

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(OUTPUT_FILENAME, fourcc, FPS, SCREEN_SIZE)

    while recording:
        # Capture the screen
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)

        # Convert RGB to BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Write the frame to the video
        out.write(frame)

    # Release the VideoWriter and destroy any OpenCV windows
    out.release()
    cv2.destroyAllWindows()

# Start recording in a separate thread
recording_thread = threading.Thread(target=record_screen)
recording_thread.start()

# Wait for user input to stop recording
input("Press Enter to stop recording...")

# Stop recording
recording = False
recording_thread.join()

print("Recording stopped. Video saved as", OUTPUT_FILENAME)
