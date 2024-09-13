import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

import numpy as np

import threading
import time

class GStreamerWrapper:
    def __init__(self):
        ##############
        #init pipeline
        ##############
        Gst.init(None)

        # pull from a device and convert with nvvidconv
        # self.pipeline_str = "v4l2src device=/dev/video0 ! video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink name=sink"
        
        # pull from a device and convert with videoconvert
        # self.pipeline_str = "v4l2src device=/dev/video0 ! video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! videoconvert ! video/x-raw,format=BGR ! appsink name=sink"
        
        # pull from a rtsp address and decode with nvv4l2decoder
        self.pipeline_str = "rtspsrc location=rtsp://192.168.1.120:8554/test ! rtph264depay ! h264parse config-interval=1 ! nvv4l2decoder ! video/x-raw(memory:NVMM) ! nvvidconv ! video/x-raw,format=BGRx ! videoscale ! video/x-raw,width=640,height=360 ! videoconvert ! video/x-raw,format=BGR ! queue max-size-buffers=5 max-size-bytes=0 max-size-time=50000000 leaky=downstream ! appsink name=sink sync=false max-buffers=1 drop=1"
        
        # init pipeline
        self.pipeline = Gst.parse_launch(self.pipeline_str)
        self.pipeline.set_state(Gst.State.PLAYING)
        self.sink = self.pipeline.get_by_name('sink')
        self.sink.set_property("emit-signals", True)

        ###############
        #get frame size
        ###############
        sample = self.sink.emit('pull-sample')
        caps = sample.get_caps()
        structure = caps.get_structure(0)
        self.width = structure.get_value('width')
        self.height = structure.get_value('height')

        self.break_flag = False
        self.get_frame_thread = threading.Thread(target=self.GetFrameThreadFunc)
        self.lock = threading.Lock()
        self.get_frame_thread.start()

    def __del__(self):
        self.pipeline.set_state(Gst.State.NULL)

    def StopThread(self):
        self.break_flag = True
        self.get_frame_thread.join()

    def GetFrameThreadFunc(self):        
        while(self.break_flag != True):
            sample = self.sink.emit('pull-sample')
            buffer = sample.get_buffer()
            success, map_info =  buffer.map(Gst.MapFlags.READ)
            if not success:
                return None
            arr = np.frombuffer(map_info.data, dtype=np.uint8)
            buffer.unmap(map_info)
            with self.lock:
                self.frame = arr.reshape((self.height, self.width, 3))

            time.sleep(0.01)

    def GetFrame(self):
        with self.lock:
            return self.frame
