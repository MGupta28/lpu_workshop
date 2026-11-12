from setuptools import setup

package_name = 'eci150_ur_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jon Doe',
    maintainer_email='jon.doe@example.com',
    description='ECI150 Day 4, Part 3: FollowJointTrajectory action client for the UR5e.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'send_joint_trajectory = eci150_ur_control.send_joint_trajectory:main',
        ],
    },
)
