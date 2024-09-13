
import cv2
import signal

from GStreamerWrapper import GStreamerWrapper
from RobotController import RobotController

break_flag = False
def set_break_flag(signum, frame):
    print("set_break_flag")
    global break_flag
    break_flag = True

signal.signal(signal.SIGINT, set_break_flag)

gstreamer_wrapper = GStreamerWrapper.GStreamerWrapper()
robot_controller = RobotController.RobotController()

while break_flag != True:
    ############
    # get frame
    ############
    bgr_frame = gstreamer_wrapper.GetFrame()
    if type(bgr_frame) == type(None):
        break

    ####################
    # control the robot
    ####################
    final_frame = robot_controller.Run(bgr_frame)

    #################
    # show final img
    #################
    cv2.imshow("DR People Tracking", final_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

gstreamer_wrapper.StopThread()

cv2.destroyAllWindows()


