"""Launch the full MentorPi Deluxe stack (body + voice + camera + Companion)."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Start vendor body, Companion brain, voice, and camera watch."""
    cfg_dir = get_package_share_directory('companion_bringup')
    deluxe_cfg = os.path.join(cfg_dir, 'config', 'mentorpi_deluxe.yaml')
    places_cfg = os.path.join(cfg_dir, 'config', 'places.yaml')
    people_cfg = os.path.join(cfg_dir, 'config', 'people.yaml')
    face_cfg = os.path.join(cfg_dir, 'config', 'face.yaml')

    show_face = LaunchConfiguration('show_face')
    enable_body = LaunchConfiguration('enable_body')

    agent_params = [deluxe_cfg, {
        'places_file': places_cfg,
        'people_file': people_cfg,
    }]
    nav_params = [deluxe_cfg, {'places_file': places_cfg}]

    return LaunchDescription([
        DeclareLaunchArgument(
            'show_face',
            default_value='false',
            description='ASCII face window (off on headless Pi by default)',
        ),
        DeclareLaunchArgument(
            'enable_body',
            default_value='true',
            description='Launch MentorPi vendor drivers (lidar, camera, motors)',
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(cfg_dir, 'launch', 'mentorpi_body.launch.py'),
            ]),
            condition=IfCondition(enable_body),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(cfg_dir, 'launch', 'perception.launch.py'),
            ]),
        ),
        Node(
            package='companion_agent',
            executable='agent_node',
            name='agent_node',
            parameters=agent_params,
            output='screen',
        ),
        Node(
            package='companion_behaviors',
            executable='behavior_controller_node',
            name='behavior_controller_node',
            parameters=[deluxe_cfg],
            output='screen',
        ),
        Node(
            package='companion_body',
            executable='nav_bridge_node',
            name='nav_bridge_node',
            parameters=nav_params,
            output='screen',
        ),
        Node(
            package='companion_body',
            executable='body_status_node',
            name='body_status_node',
            parameters=[deluxe_cfg],
            output='screen',
        ),
        Node(
            package='companion_voice',
            executable='stt_node',
            name='stt_node',
            parameters=[deluxe_cfg],
            output='screen',
        ),
        Node(
            package='companion_voice',
            executable='tts_node',
            name='tts_node',
            parameters=[deluxe_cfg],
            output='screen',
        ),
        Node(
            package='companion_face',
            executable='face_ascii_node',
            name='face_ascii_node',
            parameters=[face_cfg],
            output='screen',
            condition=IfCondition(show_face),
        ),
    ])
