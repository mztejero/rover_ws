import serial
from serial import Serial
from serial.tools import list_ports
import time
import numpy as np
import struct
import asyncio
from bleak import BleakScanner
from bleak import BleakClient

class BLEInterface:

    def __init__(self):
        board_name = "Nano 33 BLE"

        arduino_port = self.find_arduino(board_name)
        self.arduino = serial.Serial(arduino_port, baudrate=115200, timeout=0.1)
        time.sleep(2)
        self.arduino.flush()

    def find_arduino(self, device_name):
        ports = list(list_ports.comports())
        for p in ports:
            if p.description == device_name:
                return p.device

    def read_serial(self):
        mag = a = w = None
        try:
            read_msg = 'AAA\n'
            self.arduino.write(read_msg.encode('utf-8'))
            if self.arduino.in_waiting > 0:
                line = self.arduino.readline().decode('utf-8').strip()
                if line:
                    line = line.strip()
                    data = line.split(':')
                    if len(data) == 19:
                        if read_msg[0] == "A":
                            mag = np.array([float(data[2]), float(data[4]), float(data[6])])
                        if read_msg[1] == "A":
                            a = np.array([float(data[8]), float(data[10]), float(data[12])])
                        if read_msg[2] == "A":
                            w = np.array([float(data[14]), float(data[16]), float(data[18])])
                        if mag is not None and a is not None and w is not None:
                            return mag, a, w
                
        except Exception as e:
            print(f"Error in reading: {e}")

class LiDARInterface:

    def __init__(self):
        lidar_name = "CP2102 USB to UART Bridge Controller - CP2102 USB to UART Bridge Controller"
        
        lidar_port = self.find_lidar(lidar_name)
        self.lidar = serial.Serial(lidar_port, baudrate=230400, timeout=0.5)


    def find_lidar(self, device_name):
        ports = list(list_ports.comports())
        for p in ports:
            if p.description == device_name:
                print(f"device {p.description} found on port {p.device}")
                return p.device

    def read_raw_data(self):

        try:
            attempts = 0
            HEADER = None
            while attempts <= 50:
                # packet_1 = self.lidar.read(1)
                # packet_2 = self.lidar.read(1)
                HEADER = self.lidar.read(2) # packet_1 + packet_2

                if HEADER == b'\x54\x2C':
                    packet = HEADER + self.lidar.read(45)

                    speed_raw = float(struct.unpack_from('<H', packet, 2)[0])
                    start_angle_raw = float(struct.unpack_from('<H', packet, 4)[0]*np.pi/180/100)

                    distance_data_raw, intensity_data_raw = [], []
                    for i in range(6, 42, 3):
                        distance = float(struct.unpack_from('<H', packet, i)[0]/1000)
                        intensity = float(struct.unpack_from('<B', packet, i + 2)[0]/1000)
                        distance_data_raw.append(distance)
                        intensity_data_raw.append(intensity)

                    end_angle_raw = float(struct.unpack_from('<H', packet, 42)[0]*np.pi/180/100)
                    time_raw = int(struct.unpack_from('<H', packet, 44)[0])

                    return speed_raw, start_angle_raw, distance_data_raw, intensity_data_raw, end_angle_raw, time_raw
                attempts += 1
            return None
        except Exception as e:
            print(f"Error in reading: {e}")

class BLERCInterface:
    def callback(self, sender, data: bytearray):
        try:
            raw_values = bytearray(data)
            values = []
            for i in range(0, len(raw_values) - 1, 2):
                next = struct.unpack('<h', raw_values[i:i+2])[0]
                values.append(next)

            return values
        except Exception as e:
            print(f"Callback error: {e}")


    async def find_rc(self):
        address = "unknown"
        name = "RC"
        while address == "unknown":
            print("scanning...")
            devices = await BleakScanner.discover(timeout = 5.0)

            for d in devices:
                if d.name == name or d.name == "nimble":
                    address = d.address
                    print(f"RC found at {address} with name ``{d.name}``")
        
        client = BleakClient(address)
        connected = False
        while not connected:
            try:
                await client.connect()
                connected = True
            except Exception as e:
                print(f"Connection failed: {e}")
                print("Retrying...")
                await asyncio.sleep(2)
                
        print("Connected")
        print("Starting notify...")
        await client.start_notify(self.char_uuid, self.callback)

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Keyboard Interrupt with ^C")
        finally:
            await client.stop_notify(self.char_uuid)
            print("Stopped notify...")
            await client.disconnect()
            print("Disconnected")

# if __name__ == '__main__':
#     arduino_ble = BLEInterface()
#     ldrobot = LiDARInterface()
#     ble_rc = BLERCInterface()

class ROVER:

    def __init__(self):
        rover_name = "CP2102N USB to UART Bridge Controller"

        device_port = self.find_device(rover_name)
        self.rover = serial.Serial(device_port, baudrate=115200, timeout=0.1)
        time.sleep(2)
        self.rover.flush()

    def find_device(self, device_name):
        ports = list(list_ports.comports())
        for p in ports:
            print(f"port name: {p.description}")
            if p.description == device_name:
                return p.device
            
    def read_serial(self):
        line = self.rover.readline().decode('utf-8').strip()
        line = line.strip()
        data = line.split(':')
        return data
        # print(line)
        # print(data)

    def write_serial(self, msg):
        self.rover.write(msg.encode('utf-8'))

class BLE_Read:

    def __init__(self):
        self.char_uuid = "89674523-01ef-cdab-8967-452301efcdab"
        self.time_prev = time.time()

        self.interface = ROVER()
        rover_name = "CP2102N USB to UART Bridge Controller"
        self.interface.find_device(rover_name)

    def callback(self, sender, data: bytearray):
        try:
            raw_values = bytearray(data)
            values = []
            for i in range(0, len(raw_values) - 1, 2):
                next = struct.unpack('<h', raw_values[i:i+2])[0]
                values.append(next)

            # time_curr = time.time()

            W = 16*10^-2

            enc1 = round(values[4] * 10e-3, 2)
            enc2 = round(values[5] * 10e-3, 2)

            u_speed = round(values[0] * 10e-3 * enc1, 2)
            u_steer = round(values[3] * 10e-3 * enc2, 2)

            vr = u_speed + 0.5 * W * u_steer
            vl = u_speed - 0.5 * W * u_steer

            v1 = vr
            v2 = vr
            v3 = vl
            v4 = vl
            # print(f"u_speed: {u_speed}, u_steer: {u_steer}, vr: {vr}, vl: {vl}, v1: {v1}, v2: {v2}, v3: {v3}, v4: {v4} | vl: {enc1}, vr: {enc2}")
            v_str = f"v{v1}:{v2}:{v3}:{v4}\n"

            # self.interface.read_serial()
            self.interface.write_serial(v_str)
            # self.time_prev = time_curr
        except Exception as e:
            print(f"Callback error: {e}")


    async def find_rc(self):
        address = "unknown"
        name = "RC"
        while address == "unknown":
            print("scanning...")
            devices = await BleakScanner.discover(timeout = 5.0)

            for d in devices:
                if d.name == name or d.name == "nimble":
                    address = d.address
                    print(f"RC found at {address} with name ``{d.name}``")
        
        client = BleakClient(address)
        connected = False
        while not connected:
            try:
                await client.connect()
                connected = True
            except Exception as e:
                print(f"Connection failed: {e}")
                print("Retrying...")
                await asyncio.sleep(2)
                
        print("Connected")
        print("Starting notify...")
        await client.start_notify(self.char_uuid, self.callback)

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Keyboard Interrupt with ^C")
        finally:
            await client.stop_notify(self.char_uuid)
            print("Stopped notify...")
            await client.disconnect()
            print("Disconnected")
            
def main():
    ble = BLE_Read()
    asyncio.run(ble.find_rc())

    interface = RoverSerialInterface()
    rover_name = "CP2102N USB to UART Bridge Controller"
    interface.find_device(rover_name)
    print(f"reading data")

if __name__ == "__main__":
    main()