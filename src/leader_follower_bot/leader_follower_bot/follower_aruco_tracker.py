#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class HighSpeedFollowerTracker(Node):
    def __init__(self):
        super().__init__('follower_aruco_tracker')
        
        self.bridge = CvBridge()
        
        self.image_sub = self.create_subscription(
            Image,
            '/follower/camera/image_raw',
            self.image_callback,
            10)
            
        self.cmd_pub = self.create_publisher(
            Twist,
            '/follower/cmd_vel',
            10)

        # OpenCV 4.7+ modern ArucoDetector initialization
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        
        # Target sizing and velocity bounds
        self.target_pixel_width = 75.0
        
        self.curr_lin_x = 0.0
        self.curr_ang_z = 0.0
        
        self.get_logger().info('High-Speed Responsive Follower Tracker Active!')

    def image_callback(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'CvBridge Exception: {e}')
            return

        h, w, _ = frame.shape
        center_x_img = w / 2.0
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. Modern ArUco Marker Detection API
        corners, ids, rejected = self.detector.detectMarkers(gray)
        
        target_locked = False
        target_lin_x = 0.0
        target_ang_z = 0.0
        
        if ids is not None and len(ids) > 0:
            target_locked = True
            c = corners[0][0]
            cx = float(np.mean(c[:, 0]))
            
            # Width calculation based on corner distance
            marker_w = float(np.linalg.norm(c[0] - c[1]))
            
            error_x = center_x_img - cx
            dist_error = self.target_pixel_width - marker_w
            
            # Proportional Control Gains
            target_ang_z = 0.010 * error_x
            target_lin_x = max(0.0, min(0.60, 0.015 * dist_error))
        else:
            # 2. High-Contrast Fallback: Dark Plate Contour Tracking
            _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            valid_cnts = [cnt for cnt in contours if cv2.contourArea(cnt) > 80]
            
            if valid_cnts:
                largest = max(valid_cnts, key=cv2.contourArea)
                M = cv2.moments(largest)
                if M['m00'] > 0:
                    target_locked = True
                    cx = M['m10'] / M['m00']
                    area = cv2.contourArea(largest)
                    
                    error_x = center_x_img - cx
                    target_ang_z = 0.008 * error_x
                    
                    # Stepped pursuit based on target size
                    if area < 6000:
                        target_lin_x = 0.50
                    elif area < 12000:
                        target_lin_x = 0.25
                    else:
                        target_lin_x = 0.0

        if not target_locked:
            # Fail-Safe: Stop linear movement and rotate to search
            target_lin_x = 0.0
            target_ang_z = 0.30

        # Exponential Moving Average (EMA) smoothing for smooth motion
        alpha = 0.35
        self.curr_lin_x = (1.0 - alpha) * self.curr_lin_x + alpha * target_lin_x
        self.curr_ang_z = (1.0 - alpha) * self.curr_ang_z + alpha * target_ang_z

        cmd = Twist()
        cmd.linear.x = float(self.curr_lin_x)
        cmd.angular.z = float(self.curr_ang_z)
        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = HighSpeedFollowerTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
