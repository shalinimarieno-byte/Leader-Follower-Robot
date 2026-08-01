#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class StateMachineLeaderController(Node):
    def __init__(self):
        super().__init__('leader_obstacle_avoidance')
        
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/leader/scan',
            self.scan_callback,
            10)
        
        self.cmd_pub = self.create_publisher(
            Twist,
            '/leader/cmd_vel',
            10)
            
        self.timer = self.create_timer(0.05, self.control_loop)
        
        self.min_front = 10.0
        self.min_left = 10.0
        self.min_right = 10.0
        
        # State Machine Variables
        self.state = "CRUISE"  # "CRUISE" or "TURNING"
        self.turn_direction = -1.0  # -1 for Right, +1 for Left
        
        self.get_logger().info('Smooth State-Machine Leader Controller Active!')

    def scan_callback(self, msg: LaserScan):
        ranges = msg.ranges
        n = len(ranges)
        if n < 360:
            return

        mid = n // 2
        w = n // 10

        front_pts = [r for r in ranges[mid - w : mid + w] if msg.range_min < r < msg.range_max]
        left_pts = [r for r in ranges[mid + w : mid + 4*w] if msg.range_min < r < msg.range_max]
        right_pts = [r for r in ranges[mid - 4*w : mid - w] if msg.range_min < r < msg.range_max]

        self.min_front = min(front_pts) if front_pts else 10.0
        self.min_left = min(left_pts) if left_pts else 10.0
        self.min_right = min(right_pts) if right_pts else 10.0

    def control_loop(self):
        cmd = Twist()
        
        if self.state == "CRUISE":
            if self.min_front < 1.2:
                # Switch to TURNING state and lock turn direction
                self.state = "TURNING"
                self.turn_direction = -0.6 if self.min_left < self.min_right else 0.6
                cmd.linear.x = 0.10
                cmd.angular.z = self.turn_direction
            else:
                cmd.linear.x = 0.35
                cmd.angular.z = 0.0

        elif self.state == "TURNING":
            # Continue turning until front clearance reaches > 1.8 meters
            if self.min_front > 1.8:
                self.state = "CRUISE"
                cmd.linear.x = 0.35
                cmd.angular.z = 0.0
            else:
                cmd.linear.x = 0.12
                cmd.angular.z = self.turn_direction

        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = StateMachineLeaderController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()