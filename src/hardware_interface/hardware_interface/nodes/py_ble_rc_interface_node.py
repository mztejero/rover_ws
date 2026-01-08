#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from msg_types.msg import RoverData

import numpy as np
import asyncio
from hardware_interface.lib.hardware_lib import ROVER, BLE_Read

class RoverInterfaceNode(Node):

    def __init__(self):
        super().__init__("py_imu_wheel_data_interface_node")

        ble = BLE_Read()
        asyncio.run(ble.find_rc())

def main(args = None):
    rclpy.init(args = args)
    node = RoverInterfaceNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()