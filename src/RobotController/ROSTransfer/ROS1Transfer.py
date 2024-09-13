
import rospy
from geometry_msgs.msg import Twist

class ROS1Transfer:
    def __init__(self):
        rospy.init_node('track_twist_publisher')
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

    def SendCmdVel(self, linear_velocity, radian_velocity):
        twist_cmd = Twist()
        twist_cmd.linear.x = linear_velocity
        twist_cmd.angular.z = radian_velocity
        self.cmd_vel_pub.publish(twist_cmd)
        
