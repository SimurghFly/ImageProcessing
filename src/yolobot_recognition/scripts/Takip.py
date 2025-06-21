import asyncio
from mavsdk import System
from mavsdk.offboard import Attitude
from geometry_msgs.msg import Vector3

from control import PIDControl3d

class Takip(Node):
    def __init__(self):
        super().__init__('takip_node')

        asyncio.create_task(self.startup())
        self.startPid()

        self.subscription = self.create_subscription(
            Vector3,
            '/object_offset',
            self.callback_offset,
            10)

    async def startup(self):
        await self.connect_drone()
        await self.startOffboard()

    def callback_offset(self, msg):
        self.target = (msg.x, msg.y, msg.z)
        res = self.pid.one_shot(self.target) 
        yaw, pitch, distance = (res[0]*self.pid.dt, res[1]*self.pid.dt, res[2]*self.pid.dt)
        asyncio.create_task(self.distanceCheck(distance))
        asyncio.create_task(self.yawPitchUpdate(yaw, pitch))
        


    async def connect_drone(self):
        SYSTEMADRESS = "udp://:14540"

        drone = System()
        await drone.connect(system_address=SYSTEMADRESS)

        print("Bağlantı kurulması bekleniyor...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print("✅ Drone bağlı!")
                break

        self.drone = drone


    def startPid(self):
        wanted = (0,0,10)
        Ks = (1,0,0)
        self.pid = PIDControl3d(wanted, Ks)

        # pid.yawPidControl.Ks = (1,1,1) falan yapacaz


    async def startOffboard(self):
        async for euler in self.drone.telemetry.attitude_euler():
            roll = euler.roll_deg
            pitch = euler.pitch_deg
            yaw = euler.yaw_deg
            break

        self.attitude = Attitude(roll, pitch, yaw, 0.6)
        await self.drone.offboard.set_attitude(self.attitude)
        await self.drone.offboard.start()


    async def distanceCheck(self, distance):
        min_thrust = 0.4

        if distance < 0: # çok büyük görüntü
            if self.attitude.thrust_value - 0.01 > min_thrust:
                self.attitude.thrust_value -= 0.01
                await self.drone.offboard.set_attitude(self.attitude)
            else:
                pass
                # dön
                # dönme işi bitince
                # self.pid.clear()
                # self.startOffboard() 

    async def yawPitchUpdate(self, yaw_c, pitch_c):
        async for euler in self.drone.telemetry.attitude_euler():
            roll = euler.roll_deg
            pitch = euler.pitch_deg
            yaw = euler.yaw_deg
            break

        self.attitude = Attitude(roll, pitch-pitch_c, yaw-yaw_c, 0.6)
        await self.drone.offboard.set_attitude(self.attitude)