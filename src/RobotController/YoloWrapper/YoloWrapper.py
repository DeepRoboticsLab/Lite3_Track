from ultralytics import YOLO
from . import CocoTypeId

class YoloWrapper:
    def __init__(self):
        self.model = YOLO('../model/yolov8n_arm.engine')

    def Track(self, img):
        return self.model.track(img, persist=True, classes=[CocoTypeId.kPerson], conf=0.5)
