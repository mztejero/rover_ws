from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    nodes = [
        Node(
            package = "hardware_interface",
            executable = "py_ble_rc_interface_node",
            name = "ble_node",
            output = "screen"
        ),
        Node(
            package = "hardware_interface",
            executable = "py_rover_interface_node",
            name = "uart_node",
            output = "screen"
        )
    ]

    ld = LaunchDescription(nodes)

    return ld