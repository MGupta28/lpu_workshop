"""Part 2: show the UR5e in RViz with joint sliders.

This is a *wrapper*: it does not contain any robot model itself. It simply
includes the official launch file from the `ur_description` package with
ur_type:=ur5e. That upstream file starts three nodes:

  * robot_state_publisher      - reads the URDF (/robot_description) and the
                                 joint angles (/joint_states) and publishes TF.
  * joint_state_publisher_gui  - a window with one slider per joint; moving a
                                 slider publishes a new /joint_states message.
  * rviz2                      - the 3-D viewer.

Usage:
  ros2 launch eci150_ur_bringup view_ur5e.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
# AnyLaunchDescriptionSource can load both .launch.xml and .launch.py files.
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def include_upstream_view(context, *args, **kwargs):
    """Pick view_ur.launch.xml (preferred) or view_ur.launch.py, whichever exists."""
    launch_dir = os.path.join(get_package_share_directory('ur_description'), 'launch')
    xml_file = os.path.join(launch_dir, 'view_ur.launch.xml')
    py_file = os.path.join(launch_dir, 'view_ur.launch.py')
    upstream = xml_file if os.path.exists(xml_file) else py_file

    return [IncludeLaunchDescription(
        AnyLaunchDescriptionSource(upstream),
        launch_arguments={'ur_type': LaunchConfiguration('ur_type')}.items(),
    )]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('ur_type', default_value='ur5e',
                              description='UR model. The course uses ur5e.'),
        OpaqueFunction(function=include_upstream_view),
    ])
