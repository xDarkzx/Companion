"""Desktop dev stack: ASCII face + mic/keyboard + agent memory — no camera required."""
import os

from ament_index_python.packages import get_package_share_directory
from companion_voice.tts_paths import discover_piper_model
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _launch_nodes(context, *args, **kwargs):
    """Build node list; optionally add USB camera + vision preview."""
    cfg_dir = get_package_share_directory('companion_bringup')
    desktop_cfg = os.path.join(cfg_dir, 'config', 'desktop_dev.yaml')
    face_cfg = os.path.join(cfg_dir, 'config', 'face.yaml')
    vision_cfg = os.path.join(cfg_dir, 'config', 'desktop_vision.yaml')
    places_cfg = os.path.join(cfg_dir, 'config', 'places.yaml')
    people_cfg = os.path.join(cfg_dir, 'config', 'people.yaml')

    fact_db = os.path.expanduser('~/.companion/facts.db')
    os.makedirs(os.path.dirname(fact_db), exist_ok=True)

    voice_mode = LaunchConfiguration('voice_mode').perform(context)
    enable_vision = LaunchConfiguration('enable_vision').perform(context) == 'true'
    piper_model = LaunchConfiguration('piper_model').perform(context).strip()
    resolved_piper = discover_piper_model(piper_model)
    voice_share = get_package_share_directory('companion_voice')
    phrase_assets = os.path.join(voice_share, 'assets', 'phrases')
    companion_root = os.environ.get('COMPANION_ROOT', '').strip()
    if companion_root:
        alt = os.path.join(companion_root, 'assets', 'phrases')
        if os.path.isdir(alt):
            phrase_assets = alt

    face_share = get_package_share_directory('companion_face')
    user_sfx = os.path.expanduser('~/companion/sfx')
    if os.path.isdir(user_sfx):
        sfx_assets_dir = user_sfx
    else:
        sfx_assets_dir = os.path.join(face_share, 'assets', 'sfx')

    tts_params = [desktop_cfg, {'phrase_assets_dir': phrase_assets}]
    if resolved_piper:
        tts_params.append({'piper_model': resolved_piper})

    face_params = [
        desktop_cfg,
        face_cfg,
        {'sfx_assets_dir': sfx_assets_dir},
    ]

    agent_params = [
        desktop_cfg,
        {
            'places_file': places_cfg,
            'people_file': people_cfg,
            'fact_db_path': fact_db,
        },
    ]
    if enable_vision:
        agent_params.append(vision_cfg)

    detector_params = [vision_cfg] if enable_vision else []

    nodes = [
        Node(
            package='companion_voice',
            executable='stt_node',
            name='stt_node',
            parameters=[desktop_cfg, {'mode': voice_mode}],
            output='screen',
        ),
        Node(
            package='companion_voice',
            executable='tts_node',
            name='tts_node',
            parameters=tts_params,
            output='screen',
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
            parameters=[desktop_cfg],
            output='screen',
        ),
        Node(
            package='companion_body',
            executable='nav_bridge_node',
            name='nav_bridge_node',
            parameters=[desktop_cfg, {'places_file': places_cfg}],
            output='screen',
        ),
        Node(
            package='companion_body',
            executable='body_status_node',
            name='body_status_node',
            parameters=[desktop_cfg],
            output='screen',
        ),
        Node(
            package='companion_face',
            executable='face_ascii_node',
            name='face_ascii_node',
            parameters=face_params,
            output='screen',
        ),
    ]

    if enable_vision:
        nodes.extend([
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    os.path.join(cfg_dir, 'launch', 'usb_camera.launch.py'),
                ]),
            ),
            Node(
                package='companion_perception',
                executable='grounded_detector_node',
                name='grounded_detector_node',
                parameters=detector_params,
                output='screen',
            ),
            Node(
                package='companion_perception',
                executable='camera_watch_node',
                name='camera_watch_node',
                parameters=[vision_cfg],
                output='screen',
            ),
            Node(
                package='companion_face',
                executable='vision_preview_node',
                name='vision_preview_node',
                parameters=[vision_cfg, desktop_cfg],
                output='screen',
            ),
        ])

    return nodes


def generate_launch_description():
    """Start the PC prototype stack with optional USB vision."""
    return LaunchDescription([
        DeclareLaunchArgument(
            'voice_mode',
            default_value='whisper',
            description='STT: whisper (mic) or keyboard (type)',
        ),
        DeclareLaunchArgument(
            'enable_vision',
            default_value='false',
            description='Launch USB webcam + detector + vision preview window',
        ),
        DeclareLaunchArgument(
            'piper_model',
            default_value='',
            description='Piper ONNX voice model (install via scripts/desktop_install_piper.sh)',
        ),
        OpaqueFunction(function=_launch_nodes),
    ])
