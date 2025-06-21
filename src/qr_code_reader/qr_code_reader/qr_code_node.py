import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class QRCodeReader(Node):
    def __init__(self):
        super().__init__('qr_code_reader')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',  # Gazebo veya simülasyondaki kamera topic'i
            self.image_callback,
            10)
        self.br = CvBridge()
        self.qr_detector = cv2.QRCodeDetector()

    def image_callback(self, msg):
        frame = self.br.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        data, bbox, _ = self.qr_detector.detectAndDecode(frame)

        if data:
            self.get_logger().info(f'QR Code detected: {data}')
        else:
            self.get_logger().info('No QR code detected.')

def main(args=None):
    rclpy.init(args=args)
    node = QRCodeReader()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
