from setuptools import find_packages, setup

package_name = 'hardware_interface'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mztejero',
    maintainer_email='mztejero@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "py_rover_interface_node = hardware_interface.nodes.py_rover_interface_node:main",
            "py_ble_rc_interface_node = hardware_interface.nodes.py_ble_rc_interface_node:main"
        ],
    },
)
