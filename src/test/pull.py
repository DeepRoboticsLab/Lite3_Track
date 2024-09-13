import gi
import numpy as np

gi.require_version('Gst', '1.0')
from gi.repository import Gst
from gi.repository import GLib

import cv2

# Initialize GStreamer
Gst.init(None)

# GStreamer pipeline string

#pipeline_str = "v4l2src device=/dev/video6 ! video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink name=sink"

#pipeline_str = "v4l2src device=/dev/video6 ! video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! videoconvert ! video/x-raw,format=BGR ! appsink name=sink"

pipeline_str = "rtspsrc location=rtsp://192.168.1.120:8554/test ! rtph264depay ! h264parse ! nvv4l2decoder ! video/x-raw(memory:NVMM) ! nvvidconv ! video/x-raw,format=BGRx ! videoscale ! video/x-raw,width=1280,height=720 ! videoconvert ! video/x-raw,format=BGR ! queue2 max-size-buffers=5 max-size-bytes=0 max-size-time=50000000 ! appsink name=sink sync=false"

# Create the pipeline
pipeline = Gst.parse_launch(pipeline_str)
pipeline.set_state(Gst.State.PLAYING)

# Get the sink element
sink = pipeline.get_by_name('sink')
sink.set_property("emit-signals", True)

while True:
    # Emit 'pull-sample' signal to get the sample
    sample = sink.emit('pull-sample')
    
    # Retrieve the buffer
    buffer = sample.get_buffer()
    
    # Map the buffer for read access
    success, map_info = buffer.map(Gst.MapFlags.READ)
    
    if not success:
        break
    
    # Get the buffer data as bytes
    data = map_info.data
    
    # Create a numpy array from the buffer data
    arr = np.frombuffer(data, dtype=np.uint8)

    # 获取视频流的高度和宽度
    caps = sample.get_caps()
    structure = caps.get_structure(0)
    width = structure.get_value('width')
    height = structure.get_value('height')

    # Reshape the array to match the frame size
    img_bgr = arr.reshape((height, width, 3))
    
    # Display the image
    cv2.imshow("Video", img_bgr)
    
    # Wait for 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up resources
cv2.destroyAllWindows()
pipeline.set_state(Gst.State.NULL)


