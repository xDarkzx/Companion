from setuptools import find_packages, setup

package_name = 'companion_face'

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
    description="The face: turns the robot's emotion into something visible (stub in Phase 1).",
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'face_stub_node = companion_face.face_stub_node:main',
        ],
    },
)
