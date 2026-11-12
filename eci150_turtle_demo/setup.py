from glob import glob

from setuptools import setup

package_name = 'eci150_turtle_demo'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        # These two entries let ROS 2 tools (ros2 run / ros2 launch) find the package.
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install every launch file so `ros2 launch eci150_turtle_demo ...` works.
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jon Doe',
    maintainer_email='jon.doe@example.com',
    description='ECI150 Day 4, Part 1: turtlesim publisher/subscriber demo.',
    license='Apache-2.0',
    entry_points={
        # "console_scripts" turn Python functions into commands for `ros2 run`.
        'console_scripts': [
            'circle_publisher = eci150_turtle_demo.circle_publisher:main',
            'pose_subscriber = eci150_turtle_demo.pose_subscriber:main',
        ],
    },
)
