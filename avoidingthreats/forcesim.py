#gpt yazdı

import time
import numpy as np
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)

v = 15
t = 10
kucultme_orani = t*v*1.2

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
    await drone.connect()

    # Check connection status
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Bağlantı başarılı!")
            break

    return drone

async def arm_and_takeoff(drone, altitude):
    print("Motorlar arm ediliyor...")
    while not await drone.is_armable():
        print("İHA arm edilebilir değil, bekleniyor...")
        await asyncio.sleep(1)

    await drone.set_arm(True)
    
    while not await drone.is_armed():
        print("Motorlar açılıyor...")
        await asyncio.sleep(1)

    print("Kalkış başlıyor!")
    await drone.offboard.set_position_ned(PositionNedYaw(0, 0, -altitude))
    await asyncio.sleep(10)  # Simulate takeoff time

    print("Kalkış tamamlandı!")

async def move_with_apf(drone):
    target = [10, 10]  # APF hedefi (örnek)
    obstacles = [[[3, 3], [2, 0]]]

    lastcommand = 0
    while True:
        if time.time() - lastcommand < 10:
            continue

        # Mevcut konum
        current_location = await drone.telemetry.position()
        pos = [current_location.latitude / kucultme_orani, current_location.longitude / kucultme_orani]

        # APF kuvvetini hesapla
        force = await total(pos, target, obstacles)
        print(f"Kuvvet: {force}")

        # Kuvveti pozisyona dönüştür
        new_lat = (pos[0] + force[0]) * kucultme_orani
        new_lon = (pos[1] + force[1]) * kucultme_orani

        # Yeni konuma git
        await drone.offboard.set_position_ned(PositionNedYaw(new_lat, new_lon, -10))
        lastcommand = time.time()
        print(f"Yeni konuma gidiliyor: Lat={new_lat}, Lon={new_lon}")

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
        await drone.set_land(True)
        await drone.close()

if __name__ == "__main__":
    asyncio.run(main())
