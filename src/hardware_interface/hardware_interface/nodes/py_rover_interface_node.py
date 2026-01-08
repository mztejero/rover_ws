#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from msg_types.msg import RoverData

import numpy as np
import asyncio
from hardware_interface.lib.hardware_lib import ROVER

class RoverInterfaceNode(Node):

    def __init__(self):
        super().__init__("py_imu_wheel_data_interface_node")

        self.dt = 0.001

        self.rover = ROVER()
        self.rover_data = self.create_publisher(RoverData, "/rover_data", 10)
        self.timer = self.create_timer(self.dt, self.rover_publisher)

    def rover_publisher(self):
        rover_msg = RoverData()
        outputs = self.rover.read_serial()
        # self.get_logger().info(f"serial data: {outputs}")
        if outputs is not None:
            if outputs[0] == 'd':
                if len(outputs) == 15:
                    try:
                        rover_msg.d_wheel.wheel1 = float(outputs[1])
                        rover_msg.d_wheel.wheel2 = float(outputs[2])
                        rover_msg.d_wheel.wheel3 = float(outputs[3])
                        rover_msg.d_wheel.wheel4 = float(outputs[4])

                        rover_msg.v_wheel.wheel1 = float(outputs[5])
                        rover_msg.v_wheel.wheel2 = float(outputs[6])
                        rover_msg.v_wheel.wheel3 = float(outputs[7])
                        rover_msg.v_wheel.wheel4 = float(outputs[8])

                        rover_msg.a_imu.x = float(outputs[9])
                        rover_msg.a_imu.y = float(outputs[10])
                        rover_msg.a_imu.z = float(outputs[11])

                        rover_msg.w_imu.x = float(outputs[12])
                        rover_msg.w_imu.y = float(outputs[13])
                        rover_msg.w_imu.z = float(outputs[14])
                    except Exception as e:
                        self.get_logger().info(f"error: {outputs}, {e}")

            elif outputs[0] == 'v':
                if len(outputs) == 5:
                    try:
                        rover_msg.v_wheel.wheel1 = float(outputs[1])
                        rover_msg.v_wheel.wheel2 = float(outputs[2])
                        rover_msg.v_wheel.wheel3 = float(outputs[3])
                        rover_msg.v_wheel.wheel4 = float(outputs[4])
                    except Exception as e:
                        self.get_logger().info(f"error: {outputs}, {e}")

            elif outputs[0] == 'a':
                if len(outputs) == 4:
                    try:
                        rover_msg.a_imu.x = float(outputs[1])
                        rover_msg.a_imu.y = float(outputs[2])
                        rover_msg.a_imu.z = float(outputs[3])
                    except Exception as e:
                        self.get_logger().info(f"error: {outputs}, {e}")

            elif outputs[0] == 'w':
                if len(outputs) == 4:
                    try:
                        rover_msg.w_imu.x = float(outputs[1])
                        rover_msg.w_imu.y = float(outputs[2])
                        rover_msg.w_imu.z = float(outputs[3])
                    except Exception as e:
                        self.get_logger().info(f"error: {outputs}, {e}")

            self.rover_data.publish(rover_msg)

def main(args = None):
    rclpy.init(args = args)
    node = RoverInterfaceNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()