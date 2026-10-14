from setuptools import find_packages, setup

package_name = 'companion_body'

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
    description='MentorPi vendor integration and body status.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'body_status_node = companion_body.body_status_node:main',
            'nav_bridge_node = companion_body.nav_bridge_node:main',
        ],
    },
)
