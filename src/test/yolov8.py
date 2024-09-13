import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('../../model/yolov8n_amd.engine')

# Open the video file
#video_path = "rtsp://192.168.1.120:8554/test"
video_path="/dev/video0"
cap = cv2.VideoCapture(video_path)

print("track started")
# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    print("reading frame")
    success, frame = cap.read()

    if success:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        print("tracking")
        results = model.track(frame, persist=True)

        # Visualize the results on the frame
        print("ploting")
        annotated_frame = results[0].plot()

        # Display the annotated frame
        print("showing")
        cv2.imshow("YOLOv8 Tracking", frame)
        cv2.waitKey(1)
    else:
        print("not success")
        # Break the loop if the end of the video is reached
        continue

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
