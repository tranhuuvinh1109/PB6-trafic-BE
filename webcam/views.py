from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2
from ultralytics import YOLO

def index(request):
    return render(request, 'index.html')

def stream():
    cap = cv2.VideoCapture('./assets/videos/sample7.mp4')
    
    model = YOLO('./assets/models/yolov8n.pt')
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print('error: failed to capture video')
            break
    
        success, frame = cap.read()

        if success:
            # Run YOLOv8 inference on the frame
            results = model(frame)

            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            # Display the annotated frame
            cv2.imshow("YOLOv8 Inference", annotated_frame)
            cv2.waitKey(1)

            # Detect objects using YOLOv8
            frame_with_detections = annotated_frame

            # Convert the frame to JPEG format for streaming
            image_bytes = cv2.imencode('.jpg', frame_with_detections)[1].tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n')

def video_feed(request):
    return StreamingHttpResponse(stream(), content_type="multipart/x-mixed-replace;boundary=frame")
