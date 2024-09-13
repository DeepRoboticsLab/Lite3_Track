import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class ROS2Transfer(Node):
    def __init__(self):
        rclpy.init()
        super().__init__('track_twist_publisher')
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 1)

    def SendCmdVel(self, linear_velocity, radian_velocity):
        twist_cmd = Twist()
        twist_cmd.linear.x = linear_velocity
        twist_cmd.angular.z = radian_velocity
        self.cmd_vel_pub.publish(twist_cmd)
