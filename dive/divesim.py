#gpt yazdı

import asyncio
from mavsdk.offboard import Attitude
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)
import math

SYSTEMADRESS = "udp://:14540"

yukselBaslaMetre = 28.0
maxyuksek = 90.0
dalmaAcisi = 50
targetXuzaklik = 61
targetZuzaklik = maxyuksek
targetYuzaklik = 0

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

    print("-- {maxyuksek} metreye kalkış")
    await drone.action.takeoff()
    await asyncio.sleep(10)  # Yeterince yükseğe çıkması için bekle


    print("-- Offboard başlatılıyor")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -maxyuksek, 0.0))
    await drone.offboard.start()

    dogru = True
    while dogru:
        async for pos in drone.telemetry.position():
            if pos.relative_altitude_m >= maxyuksek - 1:
                print(f">> {maxyuksek} metreye ulaşıldı: {pos.relative_altitude_m:.2f} m")
                dogru  = False
                break
        await asyncio.sleep(1)

    print("-- Pozisyon kontrolü durduruluyor")
    await drone.offboard.stop()

    print("VTOL, sabit kanat moduna geçiyor...")
    await asyncio.sleep(10) 

    
    #await drone.action.transition_to_fixedwing()
    

    async def v2():
        try:
            # 45 derece dalış başlıyor
            attitude = Attitude(0, -dalmaAcisi, 0, thrust_value=0.6)
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

    await v2()
    print("-- Offboard durduruluyor ve iniş")
    await drone.offboard.stop()
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())