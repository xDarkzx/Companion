from setuptools import find_packages, setup

package_name = 'companion_brain'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Dan',
    maintainer_email='dkstudiosnz@gmail.com',
    description="The decision-maker: chooses the robot's emotion (stub in Phase 1).",
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'heartbeat_node = companion_brain.heartbeat_node:main',
            'voice_demo_node = companion_brain.voice_demo_node:main',
            'empathy_node = companion_brain.empathy_node:main',
        ],
    },
)
