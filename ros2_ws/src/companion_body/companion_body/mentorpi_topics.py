"""Default ROS topic names for MentorPi Mailun/Ackermann deluxe kit."""

# HD depth camera (ascamera vendor stack)
RGB_IMAGE_TOPIC = '/ascamera/camera_publisher/rgb0/image'
DEPTH_IMAGE_TOPIC = '/ascamera/camera_publisher/depth0/image_raw'
CAMERA_INFO_TOPIC = '/ascamera/camera_publisher/rgb0/camera_info'

# Lidar + motion (vendor orchestrator)
LIDAR_SCAN_TOPIC = '/scan'
ODOM_TOPIC = '/odom'
CMD_VEL_TOPIC = '/cmd_vel'

# Companion status topics
CAMERA_STATUS_TOPIC = '/companion/camera_status'
NAV_STATUS_TOPIC = '/companion/nav_status'
BODY_STATUS_TOPIC = '/companion/body_status'
