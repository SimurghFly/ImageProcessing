# drone a bağlan
# pid yi başlat
# kamerayı başlat


# döngü
# kameradan verileri al ve pid ye gönder
# çok yakınsa tur at, değilse pid ye göre hareket et.

import asyncio
from mavsdk import System
from mavsdk.offboard import Attitude

from control import PIDControl3d

class Takip:
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

        self.attitude = Attitude(roll, pitch, yaw, 1)
        await self.drone.offboard.set_attitude(self.attitude)
        await self.drone.offboard.start()


    async def distanceCheck(self, distance):
        min_thrust = 0.6

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

    async def yawPitchUpdate(self, yaw, pitch):
        self.attitude.pitch_deg -= pitch
        self.attitude.yaw_deg -= yaw
        await self.drone.offboard.set_attitude(self.attitude)



    async def main(self):
        await self.connect_drone()
        await self.startOffboard()
        self.startPid()
        

        # döngü ?? bu döngü nası bitcek
        # self.target = kameradan veri al
        # yaw, pitch, distance = pid.one_shot(target)
        # await self.distanceCheck(distance)
        # await self.yawPitchUpdate(yaw, pitch)


    


if __name__ == "__main__":
    asyncio.run(main())