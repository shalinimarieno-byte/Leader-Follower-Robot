import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_path = get_package_share_directory('leader_follower_bot')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world_path = os.path.join(pkg_path, 'worlds', 'obstacle_world.sdf')
    bridge_cfg = os.path.join(pkg_path, 'config', 'bridge.yaml')

    # Process Leader Xacro
    leader_xacro = os.path.join(pkg_path, 'urdf', 'leader.urdf.xacro')
    leader_doc = xacro.process_file(leader_xacro)
    leader_desc = leader_doc.toxml()

    # Process Follower Xacro
    follower_xacro = os.path.join(pkg_path, 'urdf', 'follower.urdf.xacro')
    follower_doc = xacro.process_file(follower_xacro)
    follower_desc = follower_doc.toxml()

    # 1. Launch Gazebo Sim
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_path}'}.items(),
    )

    # 2. Leader State Publisher & Spawn
    rsp_leader = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='leader',
        parameters=[{'robot_description': leader_desc, 'use_sim_time': True}],
        output='screen'
    )
    spawn_leader = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', '/leader/robot_description', '-name', 'leader_bot', '-x', '0.0', '-y', '0.0', '-z', '0.15'],
        output='screen'
    )

    # 3. Follower State Publisher & Spawn (0.8m behind Leader)
    rsp_follower = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='follower',
        parameters=[{'robot_description': follower_desc, 'use_sim_time': True}],
        output='screen'
    )
    spawn_follower = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', '/follower/robot_description', '-name', 'follower_bot', '-x', '-0.8', '-y', '0.0', '-z', '0.15'],
        output='screen'
    )

    # 4. ROS-Gazebo Parameter Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_cfg}],
        output='screen'
    )

    # 5. Autonomous Python Controllers
    leader_node = Node(
        package='leader_follower_bot',
        executable='leader_obstacle_avoidance',
        output='screen'
    )
    follower_node = Node(
        package='leader_follower_bot',
        executable='follower_aruco_tracker',
        output='screen'
    )

    return LaunchDescription([
        gz_sim,
        rsp_leader,
        spawn_leader,
        rsp_follower,
        spawn_follower,
        bridge,
        leader_node,
        follower_node
    ])