"""Publish USB webcam frames as sensor_msgs/Image for desktop vision dev."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Start usb_cam when ros-jazzy-usb-cam is installed."""
    device = LaunchConfiguration('video_device')
    width = LaunchConfiguration('image_width')
    height = LaunchConfiguration('image_height')

    return LaunchDescription([
        DeclareLaunchArgument('video_device', default_value='/dev/video0'),
        DeclareLaunchArgument('image_width', default_value='640'),
        DeclareLaunchArgument('image_height', default_value='480'),
        Node(
            package='usb_cam',
            executable='usb_cam_node_exe',
            name='usb_cam',
            parameters=[{
                'video_device': device,
                'image_width': width,
                'image_height': height,
                'framerate': 15.0,
                'pixel_format': 'yuyv',
                'camera_name': 'desktop_usb',
                'camera_info_url': '',
            }],
            output='screen',
        ),
    ])
