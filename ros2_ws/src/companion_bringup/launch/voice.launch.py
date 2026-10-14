"""Launch STT/TTS nodes (optional voice hardware on Pi)."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Start voice bridge nodes when enable_voice is true."""
    cfg_dir = get_package_share_directory('companion_bringup')
    voice_cfg = os.path.join(cfg_dir, 'config', 'voice.yaml')
    enable = LaunchConfiguration('enable_voice')

    return LaunchDescription([
        DeclareLaunchArgument(
            'enable_voice',
            default_value='false',
            description='Launch STT/TTS voice bridge nodes',
        ),
        Node(
            package='companion_voice',
            executable='stt_node',
            name='stt_node',
            parameters=[voice_cfg],
            output='screen',
            condition=IfCondition(enable),
        ),
        Node(
            package='companion_voice',
            executable='tts_node',
            name='tts_node',
            parameters=[voice_cfg],
            output='screen',
            condition=IfCondition(enable),
        ),
    ])
