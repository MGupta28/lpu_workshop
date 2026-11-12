"""Part 3: UR5e in Gazebo Classic, controlled through ros2_control.

Wrapper around the official `ur_simulation_gazebo` launch file
`ur_sim_control.launch.py`. Upstream starts:

  * Gazebo Classic (gazebo_ros gazebo.launch.py) with an empty world
  * spawn_entity.py, which puts the robot from /robot_description into Gazebo
  * robot_state_publisher (use_sim_time: true)
  * spawners for joint_state_broadcaster and joint_trajectory_controller
  * RViz (after joint_state_broadcaster is up)

Usage:
  ros2 launch eci150_ur_bringup ur5e_gazebo.launch.py
  ros2 launch eci150_ur_bringup ur5e_gazebo.launch.py gazebo_gui:=false   # slow session
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    upstream = PathJoinSubstitution(
        [FindPackageShare('ur_simulation_gazebo'), 'launch', 'ur_sim_control.launch.py'])

    return LaunchDescription([
        DeclareLaunchArgument('ur_type', default_value='ur5e',
                              description='UR model. The course uses ur5e.'),
        DeclareLaunchArgument('gazebo_gui', default_value='true',
                              description='Open the Gazebo window (false = headless, faster).'),
        DeclareLaunchArgument('launch_rviz', default_value='true',
                              description='Open RViz.'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(upstream),
            launch_arguments={
                'ur_type': LaunchConfiguration('ur_type'),
                'initial_joint_controller': 'joint_trajectory_controller',
                'start_joint_controller': 'true',
                'gazebo_gui': LaunchConfiguration('gazebo_gui'),
                'launch_rviz': LaunchConfiguration('launch_rviz'),
            }.items(),
        ),
    ])
