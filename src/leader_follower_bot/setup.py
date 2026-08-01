import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'leader_follower_bot'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.xacro')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Developer',
    maintainer_email='user@todo.todo',
    description='ROS 2 Gazebo Leader-Follower Robot System using ArUco Marker Tracking',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'leader_obstacle_avoidance = leader_follower_bot.leader_obstacle_avoidance:main',
            'follower_aruco_tracker = leader_follower_bot.follower_aruco_tracker:main',
        ],
    },
)