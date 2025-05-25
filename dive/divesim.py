#gpt yazdı

import asyncio
from mavsdk.offboard import Attitude
from mavsdk.offboard import VelocityBodyYawspeed
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)
import math

SYSTEMADRESS = "udp://:14540"

async def run():
    drone = System()
    await drone.connect(system_address=SYSTEMADRESS)

    print("Aracın bağlantı kurması bekleniyor...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone bağlı!")
            break

    print("-- ARM ediliyor")
    await drone.action.arm()

    print("-- 100 metreye kalkış")
    await drone.action.takeoff()
    await asyncio.sleep(10)  # Yeterince yükseğe çıkması için bekle

    print("Kalkış başlıyor")
    await drone.action.takeoff()
    await asyncio.sleep(10)  # Simulate takeoff time

    print("VTOL, sabit kanat moduna geçiyor...")
    #await drone.action.transition_to_fixedwing()
    await asyncio.sleep(2)

    print("-- Offboard başlatılıyor")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -100.0, 0.0))
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Offboard başlatılamadı: {error._result.result}")
        print("-- Disarm ediliyor")
        await drone.action.disarm()
        return

    async def v1():
        print("-- 45 derece açıyla dalış")
        # 45 derece ile 100 metreden 15 metreye inmek için gereken yatay mesafe:
        height_diff = 85  # 100m'den 15m'ye
        horizontal_distance = height_diff / math.tan(math.radians(45))  # 85m
        await drone.offboard.set_position_ned(PositionNedYaw(horizontal_distance, 0.0, -15.0, 0.0))
        await asyncio.sleep(10)

        print("-- Tekrar yükselme")
        await drone.offboard.set_position_ned(PositionNedYaw(horizontal_distance*2, 0.0, -100.0, 0.0))
        await asyncio.sleep(10)

    async def v2():
        print("-- 45° burun aşağı dalış başlıyor (body velocity ile)")

        # 45° dalış için: ileri ve aşağı hız bileşenleri eşit
        dive_command = VelocityBodyYawspeed(
            forward_m_s=15.0,   # ileri doğru 15 m/s
            right_m_s=0.0,
            down_m_s=15.0,      # aşağı doğru 15 m/s → tan⁻¹(15/15) = 45°
            yawspeed_deg_s=0.0
        )

        # Offboard mod zaten başlatılmış olmalı (önceki kodda start edilmişti)
        await drone.offboard.set_velocity_body(dive_command)

        # İrtifa 15m'ye inene kadar bekle
        async for position in drone.telemetry.position():
            alt = position.relative_altitude_m
            if alt <= 15.0:
                print(f"-- 15 metreye ulaşıldı: {alt:.1f} m")
                break
            await asyncio.sleep(0.1)

        print("-- Tırmanış başlıyor")

        climb_command = VelocityBodyYawspeed(
            forward_m_s=10.0,
            right_m_s=0.0,
            down_m_s=-5.0,  # yukarı doğru 5 m/s
            yawspeed_deg_s=0.0
        )
        await drone.offboard.set_velocity_body(climb_command)

        # 100 metreye tekrar çıkana kadar bekle
        async for position in drone.telemetry.position():
            alt = position.relative_altitude_m
            if alt >= 100.0:
                print(f"-- 100 metreye ulaşıldı: {alt:.1f} m")
                break
            await asyncio.sleep(0.1)

        print("-- Tırmanış tamamlandı")

    await v2()

    print("-- Offboard durduruluyor ve iniş")
    await drone.offboard.stop()
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())
