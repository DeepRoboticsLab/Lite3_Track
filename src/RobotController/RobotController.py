
import cv2

from . FpsCounter import FpsCounter
from . YoloWrapper import YoloWrapper
from . ROSTransfer import TransferConstants

kUseRos1Transfer = True

if kUseRos1Transfer:
    from . ROSTransfer import ROS1Transfer
else:
    from . ROSTransfer import ROS2Transfer

kDefaultTrackId = 0
kDefaultTrackMode = False

class RobotController(object):
    def __init__(self):
        self.fps_counter = FpsCounter.FpsCounter()
        self.yolo_wrapper = YoloWrapper.YoloWrapper()
        if kUseRos1Transfer:
            self.ros1_transfer = ROS1Transfer.ROS1Transfer()
        else:
            self.ros2_transfer = ROS2Transfer.ROS2Transfer()
    
        self.is_tracking = kDefaultTrackMode
        self.target_id = kDefaultTrackId
        self.id_str = ""

        self.last_linear_velocity = 0.0

    def SetTargetId(self, id):
        self.target_id = id

    def GetTargetId(self):
        return self.target_id

    def SetIsTracking(self, state):
        self.is_tracking = state

    def GetIsTracking(self):
        return self.is_tracking

    def FindTarget(self, boxes):
        for box in boxes:
            if box.id != None:
                if box.id.item() == self.GetTargetId():
                    return box
    
    def InputAndProcess(self, frame):
        key = cv2.waitKey(1)
        if(self.GetIsTracking() == False):
            if key >= ord('0') and key <= ord('9'):  # 大键盘输入
                self.id_str += str((int(key - ord('0'))))
            elif key == ord('\b'):  # 退格
                self.id_str = self.id_str[:-1]
            elif key == 10 or key == 13 or key == 141:  # 回车
                if(self.id_str == ""):
                    self.SetTargetId(0)
                else:
                    self.SetTargetId(int(self.id_str))
                self.id_str = ""

            if(self.GetTargetId() != kDefaultTrackId):
                self.SetIsTracking(True)

        else:
            if key == 10 or key == 13 or key == 141:  # 回车
                self.id_str == ""
                self.target_id = 0
                self.SetIsTracking(False)
        frame = cv2.putText(frame, self.id_str, (20, 150), cv2.FONT_HERSHEY_PLAIN, 2, [255, 0, 0], 2)

    def TrackAndDraw(self, frame, box):
        shape = frame.shape
        frame = cv2.UMat(frame)

        self.fps_counter.Count()
        frame = cv2.putText(frame, "fps {:.02f}".format(self.fps_counter.GetFps()), (10, 20),
                    cv2.FONT_HERSHEY_PLAIN, 2, [0, 128, 0], 2)
        self.InputAndProcess(frame)

        if(box != None):            
            x1 = int(box.xyxy[0][0].item())
            y1 = int(box.xyxy[0][1].item())
            x2 = int(box.xyxy[0][2].item())
            y2 = int(box.xyxy[0][3].item())
            center=((x1+x2)//2, (y1+y2)//2)
            cv2.circle(frame,center,2,[0,0,255],-1) # 画出选框中心点

            #cal radian_velocity
            angle=(center[0]/shape[1]-0.5)*2        # range -1 to 1
            radian_velocity = -angle*TransferConstants.kMaxRadianVelocity

            #cal linear_velocity
            top=y1/shape[0]
            if top < 0.25:
                kp_linear_x = 5
                kd_linear_x = 0.2
                linear_velocity = top * kp_linear_x - self.last_linear_velocity * kd_linear_x
            else:
                linear_velocity=TransferConstants.kMaxLinerVelocity

            #draw
            cv2.putText(frame,"Selected ID {:}".format(self.GetTargetId()),(20,125), cv2.FONT_HERSHEY_PLAIN, 2, [255,0,0], 2)
            cv2.putText(frame,"Press \"Enter\" to reset ID",(20,150), cv2.FONT_HERSHEY_PLAIN, 2, [255,0,0], 2)
            label = '{}{:d}'.format("", self.GetTargetId())
            t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 2 , 2)[0]
            cv2.rectangle(frame, (x1, y1), (x2, y2), [255,128,128], 2)
            cv2.rectangle(frame,(x1, y1),(x1+t_size[0]+3,y1+t_size[1]+4), [255,128,128],-1)
            cv2.putText(frame,label,(x1,y1+t_size[1]+4), cv2.FONT_HERSHEY_PLAIN, 2, [255,255,255], 2)
            cv2.putText(frame,"{:.02f} m/s".format(linear_velocity),(0,250), cv2.FONT_HERSHEY_PLAIN, 2, [255,0,0], 3)
            cv2.putText(frame,"{:.02f} rad/s".format(radian_velocity),(0,300), cv2.FONT_HERSHEY_PLAIN, 2, [255,0,0], 3)

            #pub cmdvel
            if kUseRos1Transfer:
                self.ros1_transfer.SendCmdVel(linear_velocity, radian_velocity)
            else:
                self.ros2_transfer.SendCmdVel(linear_velocity, radian_velocity)
            self.last_linear_velocity = linear_velocity
            return frame
        else:
            cv2.putText(frame,"Miss Person".format(self.GetTargetId()),(20,100), cv2.FONT_HERSHEY_PLAIN, 2, [0,0,255], 3)
            cv2.putText(frame,"Press \"Enter\" to reset ID",(20,125), cv2.FONT_HERSHEY_PLAIN, 2, [255,0,0], 2)
            cv2.putText(frame,"{:.02f} m/s".format(0),(0,250), cv2.FONT_HERSHEY_PLAIN, 2, [255,0,0], 3)
            cv2.putText(frame,"{:.02f} rad/s".format(0),(0,300), cv2.FONT_HERSHEY_PLAIN, 2, [255,0,0], 3)   
            return frame

    def NonTrackAndDraw(self, frame):
        frame = cv2.UMat(frame)
        self.fps_counter.Count()
        frame = cv2.putText(frame, "fps {:.02f}".format(self.fps_counter.GetFps()), (10, 20),
                    cv2.FONT_HERSHEY_PLAIN, 2, [0, 128, 0], 2)
        self.InputAndProcess(frame)

        cv2.putText(frame,"Stop",(20,100), cv2.FONT_HERSHEY_PLAIN, 2, [0,0,255], 3)
        cv2.putText(frame,"Enter the object ID:",(20,125), cv2.FONT_HERSHEY_PLAIN, 2, [255,0,0], 2)
        cv2.putText(frame,"{:.02f} m/s".format(0),(0,250), cv2.FONT_HERSHEY_PLAIN, 2, [255,0,0], 3)
        cv2.putText(frame,"{:.02f} rad/s".format(0),(0,300), cv2.FONT_HERSHEY_PLAIN, 2, [255,0,0], 3)    
        return frame

    def Run(self, frame):
        results = self.yolo_wrapper.Track(frame)
        if(len(results)>0):
            if(self.GetIsTracking()):
                box = self.FindTarget(results[0].boxes)                
                return self.TrackAndDraw(frame, box)
            else:
                frame = results[0].plot()
                return self.NonTrackAndDraw(frame)





