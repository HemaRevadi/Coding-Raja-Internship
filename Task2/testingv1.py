from ultralytics import YOLO
import cv2

# Load the YOLOv8 model
model = YOLO('yolov8n.pt')

# Set the source of the video
source_video = "testv1.mp4"

# Perform prediction on the video
results = model.predict(source=source_video, show=True, save=True)  # 'show=False' to prevent auto-display

# Loop through the results to display them frame by frame in a resized window
for result in results:
    # Get the frame (result) from the model prediction
    frame = result.plot()  # .plot() method plots bounding boxes and labels

    # Get the dimensions of the frame
    height, width = frame.shape[:2]

    # Dynamically adjust the window size to fit the video
    cv2.namedWindow('YOLOv8 Output', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('YOLOv8 Output', min(width, 1280), min(height, 720))  # Resize to fit within 1280x720

    # Display the frame
    cv2.imshow('YOLOv8 Output', frame)

    # Wait for 1 millisecond; break if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources and close windows
cv2.destroyAllWindows()
