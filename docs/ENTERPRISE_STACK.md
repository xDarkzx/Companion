# Enterprise stack — Companion + MentorPi

Professional mobile-robot pattern used in AMR fleets, adapted for the emotion companion.

## Layers

| Layer | Package / tool | Role |
|-------|----------------|------|
| OS | Ubuntu Server 24.04 | Pi brain |
| Middleware | ROS 2 **Jazzy** | Topics, actions, launch |
| **Companion brain** | `companion_brain`, `companion_face` | Emotion, personality, face, SFX |
| **Companion agent** | `companion_agent` | Voice/text → multi-step plans |
| **Companion memory** | `companion_memory` | Named places + people YAML |
| **Companion behaviors** | `companion_behaviors` | follow, patrol, go_to_place → emotion + patrol animations |
| **Companion voice** | `companion_voice` | STT/TTS USB audio bridge |
| **Companion body** | `companion_body` | `nav_bridge_node` → `/goal_pose`, vendor status |
| **Vendor** | `ros2_ws/src/vendor/*` | Hiwonder motors, lidar, camera |
| Navigation | **Nav2** + `slam_toolbox` | Path plan, avoid, patrol waypoints |
| Follow | Nav2 [dynamic following](https://docs.nav2.org/tutorials/docs/navigation2_dynamic_point_following.html) | Follow me |
| Explore | `m-explore-ros2` | Wander / map unknown space |
| AI orchestration | [NASA ROSA](https://github.com/nasa-jpl/rosa) (Phase 3+) | Natural language → ROS tools |

## Message contracts

| Topic / msg | Producer | Consumer |
|-------------|----------|----------|
| `/companion/robot_emotion` (`RobotEmotion`) | brain, behaviors | face, audio |
| `/companion/behavior_request` (`BehaviorRequest`) | agent, ROSA | behaviors, nav_bridge |
| `/companion/voice_command` (`std_msgs/String`) | STT, demo | agent |
| `/goal_pose` (`geometry_msgs/PoseStamped`) | nav_bridge | Nav2 |
| `/companion/body_status` | body | bringup |
| `/cmd_vel`, `/odom`, `/scan` | vendor Nav2 | standard ROS |

## Launch entry points

```bash
# Dev stack (no hardware)
ros2 launch companion_bringup companion_stack.launch.py

# ASCII face + voice demo (Phase 2)
ros2 launch companion_bringup demo_face.launch.py

# MentorPi drivers (after vendor fetch)
ros2 launch companion_bringup mentorpi_body.launch.py
```

## Test a voice command (no mic yet)

```bash
ros2 launch companion_bringup companion_stack.launch.py
ros2 topic pub /companion/voice_command std_msgs/msg/String "{data: 'go to kitchen and patrol'}" --once
ros2 topic echo /companion/robot_emotion
ros2 topic echo /goal_pose
```

Full human-interface design: **`docs/HUMAN_INTERFACE.md`**

## Install order (Pi)

1. `docs/SETUP.md` — Ubuntu 24.04 + Jazzy
2. `bash scripts/pi_install_nav2.sh` — Nav2 + SLAM
3. `bash scripts/fetch_mentorpi_vendor.sh` — MentorPi drivers
4. `bash scripts/pi_install_voice.sh` — ALSA + Whisper (when voice box arrives)
5. `colcon build && colcon test`
6. `docs/DEPLOY_MENTORPI.md` — first boot + mapping

## What we do not build

- Motor serial protocol (vendor `driver`)
- Global planner / costmaps (Nav2)
- Custom SLAM (slam_toolbox)

## Phase map

| Phase | Delivers |
|-------|----------|
| 2 (now) | Face + agent + behavior building blocks |
| 3 | YOLO + Nav2 follow/patrol wired to behaviors |
| 3b | NASA ROSA + Whisper voice |
| 4 | rosbag fine-tuning pipeline |
