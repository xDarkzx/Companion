from setuptools import find_packages, setup

package_name = 'companion_perception'

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
    description='Vision detectors (YOLO stub until Phase 3).',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'detector_node = companion_perception.detector_node:main',
            'camera_watch_node = companion_perception.camera_watch_node:main',
            'human_emotion_stub_node = companion_perception.human_emotion_stub_node:main',
        ],
    },
)
