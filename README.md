
---

# 2. Leader-Follower Robot

This one-ku namma actual project structure based on what we checked, so this can be more specific.

```markdown
# Leader-Follower Robot

A ROS 2-based multi-robot system in which a follower robot tracks and follows a leader robot while maintaining awareness of obstacles in the environment.

The project demonstrates robot-to-robot tracking, perception, obstacle avoidance, and coordinated movement in a simulated environment.

## Features

- Leader and follower robot architecture
- ArUco-based leader tracking
- Camera-based visual perception
- Leader obstacle avoidance
- Follower tracking
- Gazebo simulation
- ROS 2 communication
- Custom robot models
- Configurable simulation environment

## Technologies Used

- ROS 2
- Python
- Gazebo
- OpenCV
- ArUco Marker Detection
- URDF / Xacro
- Camera
- LiDAR
- ROS 2 Launch System

## System Requirements

| Component | Requirement |
|---|---|
| Operating System | Ubuntu 24.04 |
| ROS 2 | Jazzy |
| Python | Python 3 |
| Gazebo | Gazebo Sim |

## Project Structure

```text
Leader-Follower-Robot/
│
└── src/
    └── leader_follower_bot/
        ├── config/
        │   └── bridge.yaml
        │
        ├── launch/
        │   └── simulation.launch.py
        │
        ├── leader_follower_bot/
        │   ├── follower_aruco_tracker.py
        │   └── leader_obstacle_avoidance.py
        │
        ├── urdf/
        │   ├── leader.urdf.xacro
        │   ├── follower.urdf.xacro
        │   ├── camera.xacro
        │   ├── lidar.xacro
        │   └── aruco_marker.xacro
        │
        ├── worlds/
        │   └── obstacle_world.sdf
        │
        ├── package.xml
        ├── setup.py
        └── setup.cfg
