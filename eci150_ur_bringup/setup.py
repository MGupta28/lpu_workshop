from glob import glob

from setuptools import setup

package_name = 'eci150_ur_bringup'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jon Doe',
    maintainer_email='jon.doe@example.com',
    description='ECI150 Day 4, Parts 2-3: launch wrappers for UR5e (RViz, Gazebo) and Panda.',
    license='Apache-2.0',
    entry_points={'console_scripts': []},
)
