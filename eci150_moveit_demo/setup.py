from setuptools import setup

package_name = 'eci150_moveit_demo'

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
    description='ECI150 Day 4, Part 4: add/remove a collision box in the Panda MoveIt demo.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'add_collision_box = eci150_moveit_demo.add_collision_box:main',
        ],
    },
)
