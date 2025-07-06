import asyncio
from mavsdk.offboard import Attitude
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)
import math

import numpy as np
from pymap3d import geodetic2ned

SYSTEMADRESS = "udp://:14540"

yukselBaslaMetre = 28.0
maxyuksek = 90.0
dalmaAcisi = 50
targetXuzaklik = 61
targetZuzaklik = maxyuksek
targetYuzaklik = 0

tolerence = 10

target = [0, -146] # north east sırasıyla

async def dive(drone):
        try:
            async for euler in drone.telemetry.attitude_euler():
                yaw = euler.yaw_deg  # Yaw değeri derece cinsinden
                print(f"Anlık Yaw: {yaw:.2f}°")
                break
            # 45 derece dalış başlıyor
            attitude = Attitude(0, -dalmaAcisi, yaw, thrust_value=0.6)
            await drone.offboard.set_attitude(attitude)
            await drone.offboard.start()
        except OffboardError as error:
            print(f"Offboard başlatılamadı: {error._result.result}")
            print("-- Disarm ediliyor")
            await drone.action.disarm()
            return

        # İrtifa 15 metreye inene kadar bekle
        async for position in drone.telemetry.position():
            alt = position.relative_altitude_m
            if alt <= yukselBaslaMetre:
                print(f"-- {yukselBaslaMetre} metreye ulaşıldı: {alt:.1f} m")
                break
            await asyncio.sleep(0.1)

        print("-- Duruş ve yükselişe geçiş")
        # Pitch sıfırlanır (düz uçuş) ve thrust artırılırac
        level_attitude = Attitude(0, 0, 0, thrust_value=0.8)
        await drone.offboard.set_attitude(level_attitude)

        # Yükselmeye başla, 100m'ye kadar devam et
        async for position in drone.telemetry.position():
            alt = position.relative_altitude_m
            if alt >= 100.0:
                print(f"-- 100 metreye tekrar ulaşıldı: {alt:.1f} m")
                break
            await asyncio.sleep(0.1)

async def main():
    drone = System()
    await drone.connect(system_address=SYSTEMADRESS)

    print("Aracın bağlantı kurması bekleniyor...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone bağlı!")
            break
    async for position in drone.telemetry.position():
        # Drone pozisyonu
        slat = position.latitude_deg
        slon = position.longitude_deg
        salt = position.absolute_altitude_m
        break

    while True:
        async for position in drone.telemetry.position():
            # Drone pozisyonu
            lat = position.latitude_deg
            lon = position.longitude_deg
            alt = position.absolute_altitude_m

            # NED dönüşümü (dronub başlangıcını'ı referans al)
            n, e, d = geodetic2ned(lat, lon, alt, slat, slon, salt) 
            print(f"n: {n}, e: {e}, lan: {lat}, lon: {lon}")
            distance = np.linalg.norm([n-target[0], e-target[1]])

            print(f"Şu anki mesafe hedefe: {distance:.2f} m")

            async for euler in drone.telemetry.attitude_euler():
                yaw = euler.yaw_deg  # Yaw değeri derece cinsinden
                print(f"Anlık Yaw: {yaw:.2f}°")
                break

            if distance <= targetXuzaklik + tolerence:
                print("✅ Drone hedefe 61 metreden fazla yaklaşmış!")
                await dive(drone)
                break

            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())