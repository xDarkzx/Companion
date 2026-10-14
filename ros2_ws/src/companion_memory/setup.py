from setuptools import find_packages, setup

package_name = 'companion_memory'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'pyyaml'],
    zip_safe=True,
    maintainer='Dan',
    maintainer_email='dkstudiosnz@gmail.com',
    description='Named places and people memory for voice commands.',
    license='Apache-2.0',
    tests_require=['pytest'],
)
