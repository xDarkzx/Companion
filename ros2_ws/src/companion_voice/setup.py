from glob import glob

from setuptools import find_packages, setup

package_name = 'companion_voice'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (
            'share/' + package_name + '/assets/phrases',
            glob('assets/phrases/*', recursive=False),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Dan',
    maintainer_email='dkstudiosnz@gmail.com',
    description='STT/TTS voice bridge (Whisper + USB audio).',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'stt_node = companion_voice.stt_node:main',
            'tts_node = companion_voice.tts_node:main',
        ],
    },
)
