import time
import math
import numpy as np
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)
from pymap3d import geodetic2ned
import asyncio

v = 15
t = 1
kucultme_orani = t*v*1.2
SYSTEMADRESS = "udp://:14540"
geo = []

async def attractive(target, pos):
    att_k = 3
    force = target - pos
    d = np.linalg.norm(force)
    force = force / d if d != 0 else np.array([1, 0])
    return force * att_k

async def repulsive(obstacles, pos):
    rep_k = 6
    n = 1.5

    total_force = np.array([0.0, 0.0])
    for obs in obstacles:
        o_pos = np.array(obs[0])
        r = obs[1][0]
        d = np.linalg.norm(o_pos - pos)
        d = d if d != 0 else 0.00001
        dr = (d - r) if (d - r) != 0 else 0.00001

        if d < r:
            rep_force = rep_k * (pos - o_pos) / d
        elif d < 10 * r:
            rep_force = rep_k * (pos - o_pos) * (1 / d) * (1 / dr**n)
        else:
            rep_force = np.array([0.0, 0.0])
        total_force += rep_force

    return total_force

async def total(pos, target, obstacles, unity=True):
    t = await repulsive(obstacles, pos) + await attractive(target, pos)
    magnitude = np.linalg.norm(t)
    return t / magnitude if (unity and magnitude != 0) else t

async def connect_vehicle():
    print("İHA'ya bağlanılıyor...")
    drone = System()
    await drone.connect(system_address=SYSTEMADRESS)

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Bağlantı başarılı!")
            break
    return drone

async def arm_and_takeoff(drone: System, altitude):
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
    await drone.action.takeoff()
    await asyncio.sleep(10)

    print("VTOL, sabit kanat moduna geçiyor...")
    # await drone.action.transition_to_fixedwing()
    await asyncio.sleep(2)

    async for position in drone.telemetry.position():
        global geo
        geo = position.latitude_deg, position.longitude_deg, position.relative_altitude_m
        break
    print("Kalkış tamamlandı!")

async def move_with_apf(drone: System):
    target = [10, 10]  # APF hedefi (örnek)
    obstacles = [[[7, 0], [2, 0]]]

    await drone.offboard.set_position_ned(PositionNedYaw(0, 0, -500, 0))
    await drone.offboard.start()

    lastcommand = 0
    while True:
        if time.time() - lastcommand < t:
            await asyncio.sleep(0.1)
            continue

        async for position in drone.telemetry.position():
            lat, lon, alt = position.latitude_deg, position.longitude_deg, position.relative_altitude_m
            ned_north, ned_east, ned_down = geodetic2ned(lat, lon, alt, geo[0], geo[1], geo[2])
            pos = [ned_east / kucultme_orani, ned_north / kucultme_orani]
            print(f"Pozisyon: {pos}")
            break

        force = await total(np.array(pos), np.array(target), obstacles)
        print(f"Kuvvet: {force}")

        new_e = (pos[0] + force[0] * 10) * kucultme_orani
        new_n = (pos[1] + force[1] * 10) * kucultme_orani

        heading_rad = math.atan2(force[0], force[1])  # east, north
        heading_deg = math.degrees(heading_rad)

        print(f"Yeni konum: N: {new_n:.2f}, E: {new_e:.2f}, Yaw: {heading_deg:.2f}")
        try:
            await drone.offboard.set_position_ned(PositionNedYaw(new_n, new_e, -500, heading_deg))
        except OffboardError as e:
            print(f"Offboard Hatası: {e}")
            await drone.offboard.stop()
            return

        lastcommand = time.time()

async def main():
    drone = await connect_vehicle()
    try:
        await arm_and_takeoff(drone, 500)
        await move_with_apf(drone)
    except KeyboardInterrupt:
        print("Görev iptal edildi.")
    finally:
        print("İniş başlatılıyor...")
        await drone.action.land()
        await asyncio.sleep(5)
asyncio.run(main())
