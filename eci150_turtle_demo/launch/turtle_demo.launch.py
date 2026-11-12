"""Part 1 launch file: turtlesim + circle_publisher + pose_subscriber.

A launch file starts several nodes with one command:
  ros2 launch eci150_turtle_demo turtle_demo.launch.py
  ros2 launch eci150_turtle_demo turtle_demo.launch.py linear_x:=2.0 angular_z:=0.8
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    linear_x = LaunchConfiguration('linear_x')
    angular_z = LaunchConfiguration('angular_z')

    return LaunchDescription([
        DeclareLaunchArgument('linear_x', default_value='1.0',
                              description='Forward speed of the turtle [m/s]'),
        DeclareLaunchArgument('angular_z', default_value='1.0',
                              description='Turning speed of the turtle [rad/s]'),

        # The simulator window. Its node name is /turtlesim.
        Node(package='turtlesim', executable='turtlesim_node',
             name='turtlesim', output='screen'),

        # Our publisher: drives the turtle in a circle.
        Node(package='eci150_turtle_demo', executable='circle_publisher',
             name='circle_publisher', output='screen',
             parameters=[{'linear_x': linear_x, 'angular_z': angular_z}]),

        # Our subscriber: prints the pose about once per second.
        Node(package='eci150_turtle_demo', executable='pose_subscriber',
             name='pose_subscriber', output='screen'),
    ])
