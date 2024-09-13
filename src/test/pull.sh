#gst-launch-1.0 rtspsrc location=rtsp://192.168.1.120:8554/test ! rtph264depay ! h264parse config-interval=1 ! nvv4l2decoder ! 'video/x-raw(memory:NVMM)' ! nvvideoconvert ! 'video/x-raw' ! autovideosink sync=false latency=0

#gst-launch-1.0 rtspsrc location=rtsp://192.168.1.120:8554/test ! rtph264depay ! h264parse ! decodebin ! videoconvert ! autovideosink sync=false latency=0

gst-launch-1.0 rtspsrc location=rtsp://192.168.1.120:8554/test ! rtph264depay ! h264parse config-interval=1 ! nvv4l2decoder ! 'video/x-raw(memory:NVMM)' ! nvvidconv ! 'video/x-raw,format=BGRx' ! videoconvert ! autovideosink sync=false async=false

