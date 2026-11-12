"""Part 2 (optional extra): show the Franka Panda in RViz with joint sliders.

There is no official "view only" launch for the Panda in MoveIt resources, so
we assemble the same three nodes that view_ur5e uses, pointing at the URDF
shipped in `moveit_resources_panda_description`.

Usage:
  ros2 launch eci150_ur_bringup view_panda.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # The URDF is a plain XML text file; robot_state_publisher wants its text.
    urdf_file = os.path.join(
        get_package_share_directory('moveit_resources_panda_description'),
        'urdf', 'panda.urdf')
    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    rviz_config = os.path.join(
        get_package_share_directory('eci150_ur_bringup'), 'rviz', 'panda_view.rviz')

    return LaunchDescription([
        # Publishes TF for every link from the URDF + current joint angles.
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': robot_description}], output='screen'),
        # Slider window that publishes /joint_states.
        Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui'),
        # 3-D viewer. Fixed Frame is panda_link0 (the Panda base).
        Node(package='rviz2', executable='rviz2', arguments=['-d', rviz_config]),
    ])
