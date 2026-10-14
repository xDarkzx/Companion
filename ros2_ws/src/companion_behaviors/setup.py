from setuptools import find_packages, setup

package_name = 'companion_behaviors'

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
    description='High-level behaviors: follow, patrol, harass-dog, etc.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'behavior_controller_node = '
            'companion_behaviors.behavior_controller_node:main',
        ],
    },
)
