from setuptools import find_packages, setup

package_name = 'companion_vision'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'numpy'],
    extras_require={
        'models': ['torch', 'transformers>=4.57,<5', 'pillow'],
        'demo': ['opencv-python'],
    },
    zip_safe=True,
    maintainer='Dan',
    maintainer_email='dkstudiosnz@gmail.com',
    description='ROS-free perception: open-vocabulary detection, depth and 3D localisation.',
    license='Apache-2.0',
    tests_require=['pytest'],
)
