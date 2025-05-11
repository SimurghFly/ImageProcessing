#gpt yazdı

import time
import numpy as np
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)

v = 15
t = 1
kucultme_orani = t*v*5
SYSTEMADRESS = "udp://:14540"

async def attractive(target, pos):
    att_k = 3
    force = target - pos
    d = np.linalg.norm(force - np.array([0,0]))
    force = force / d
    return force * att_k

async def repulsive(obstacles, pos):
    d0 = 1
    rep_k = 6
    k = 100
    n = 1.5  # The bigger n is, the more rapidly the force decreases

    total_force = np.array([0, 0])
    for obs in obstacles:
        o_pos = np.array(obs[0])
        r = obs[1][0]
        d = np.linalg.norm(o_pos - pos)
        if d == 0:
            d = 0.00001
        dr = d - r
        if dr == 0:
            dr = 0.00001

        if d < r:
            rep_force = rep_k * (pos - o_pos) / d
        elif d < 10*r: 
            rep_force = rep_k * (pos - o_pos) * (1/d) * (1 / dr**n)
        else: 
            rep_force = pos - pos # 0,0

        total_force = total_force + rep_force
    
    return total_force

async def total(pos, target, obstacles, unity=True):
    t = await repulsive(obstacles, pos) + await attractive(target, pos)
    magnitude = ((t[0]**2 + t[1]**2)**0.5)
    if magnitude == 0:
        return (np.array([1,0]))   
    return t / magnitude if unity else t  

# İHA Bağlantısı
async def connect_vehicle():
    print("İHA'ya bağlanılıyor...")
    drone = System()
    await drone.connect(system_address=SYSTEMADRESS)

    # Check connection status
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Bağlantı başarılı!")
            break

    return drone

async def arm_and_takeoff(drone : System, altitude):
    print("Motorlar arm ediliyor...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_armable:
            print("Drone hazır, motorlar açılıyor...")
            break
        await asyncio.sleep(1)

    await drone.action.arm()
    
    async for state in drone.telemetry.armed():
        if state:
            print("Drone armlandı!")
            break
        await asyncio.sleep(1)

    print("Kalkış başlıyor!")
    #await drone.action.set_takeoff_altitude(altitude) sabitkanatsa bunu kullan
    await drone.action.takeoff()
    await asyncio.sleep(10)  # Simulate takeoff time

    print("VTOL, sabit kanat moduna geçiyor...")
    # await drone.action.transition_to_fixedwing()
    await asyncio.sleep(2)


    print("Kalkış tamamlandı!")

async def move_with_apf(drone : System):
    target = [2.48, 1.4]  # APF hedefi (örnek)
    obstacles = [[[1.49, 0.1], [0.1, 0]]]

    await drone.offboard.set_position_ned(PositionNedYaw(0, 0, -10, 0))
    await drone.offboard.start()

    lastcommand = 0
    while True:
        if time.time() - lastcommand < t:
            await asyncio.sleep(1)

        await asyncio.sleep(1)

        # Mevcut konum
        async for position in drone.telemetry.position():
            print(position)
            pos = [position.latitude_deg / kucultme_orani, 
                   position.longitude_deg / kucultme_orani]  
            break

        # APF kuvvetini hesapla
        force = await total(np.array(pos), np.array(target), obstacles)
        print(f"Kuvvet: {force}")

        # Kuvveti pozisyona dönüştür
        new_lat = (pos[0] + force[0]*5) * kucultme_orani
        new_lon = (pos[1] + force[1]*5) * kucultme_orani

        print(f"Yeni konuma gidiliyor: Lat={new_lat}, Lon={new_lon}")
        try:
            await drone.offboard.set_position_ned(PositionNedYaw(new_lat, new_lon, -10, 0))
        except OffboardError as e:
            print(f"Offboard Hatası: {e}")
            await drone.offboard.stop()
            return
        lastcommand = time.time()

# Ana çalışma fonksiyonu
import asyncio

async def main():
    drone = await connect_vehicle()
    
    try:
        await arm_and_takeoff(drone, 10)  # 10 metreye kalk
        await move_with_apf(drone)
    except KeyboardInterrupt:
        print("Görev iptal edildi.")
    finally:
        print("İniş başlatılıyor...")
        await drone.action.land()
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
