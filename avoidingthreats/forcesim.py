#gpt yazdı

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import numpy as np

v = 15
t = 10
kucultme_orani = t*v*1.2

def attractive(target, pos):
    att_k = 3

    force = target - pos
    d = np.linalg.norm(force - np.array([0,0]))
    force = force / d

    return force * att_k

def repulsive(obstacles, pos):
    d0 = 1
    rep_k = 6
    k = 100
    n = 1.5 # The bigger n is, the more rapidly the force decreases

    # Every obstacle is like [[x,y],[r, 0]]
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
        elif d < 10*r: # 10r means everywhere
            # It can be better to use r + d0 instead of 10r
            rep_force = rep_k * (pos - o_pos) * (1/d) * (1 / dr**n)
            # rep_force = rep_k * (pos - o_pos) * r / d * 
        else: 
            rep_force = pos - pos # 0,0

        total_force = total_force + rep_force
    
    return total_force

# WE'LL NEED REPULSIVE FORCE FOR EDGES OF THE ZONE

def total(pos, target, obstacles, unity = True):
    t = repulsive(obstacles, pos) + attractive(target, pos)
    magnitude = ((t[0]**2 + t[1]**2)**0.5)
    if magnitude == 0:
        return (np.array([1,0]))   
    return t / magnitude if unity else t  # + duvarların ititci kuvveti

# İHA Bağlantısı
print("İHA'ya bağlanılıyor...")
vehicle = connect('udp:127.0.0.1:14550', wait_ready=True)

# Kalkış fonksiyonu
def arm_and_takeoff(altitude):
    print("Motorlar arm ediliyor...")
    while not vehicle.is_armable:
        print("İHA arm edilebilir değil, bekleniyor...")
        time.sleep(1)

    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print("Motorlar açılıyor...")
        time.sleep(1)

    print("Kalkış başlıyor!")
    vehicle.simple_takeoff(altitude)

    while True:
        print(f"Yükseklik: {vehicle.location.global_relative_frame.alt:.2f} m")
        if vehicle.location.global_relative_frame.alt >= altitude * 0.95:
            print("Hedef yüksekliğe ulaşıldı!")
            break
        time.sleep(1)

# Yeni hedef konum belirleme (APF ile)
def move_with_apf():
    # Hedef ve engeller
    target = [10, 10]  # APF hedefi (örnek)
    obstacles = [[[3, 3], [2, 0]]]

    lastcommand = 0
    while True:
        if time.time() - lastcommand < 10:
            continue

        # Mevcut konum
        current_location = vehicle.location.global_relative_frame
        pos = [current_location.lat / kucultme_orani, current_location.lon / kucultme_orani]

        # APF kuvvetini hesapla
        force = total(pos, target, obstacles)
        print(f"Kuvvet: {force}")

        # Kuvveti pozisyona dönüştür
        new_lat = (pos[0] + force[0]) * kucultme_orani
        new_lon = (pos[1] + force[1]) * kucultme_orani

        # Yeni konuma git
        new_location = LocationGlobalRelative(new_lat, new_lon, 10)
        vehicle.simple_goto(new_location)
        lastcommand = time.time()
        print(f"Yeni konuma gidiliyor: Lat={new_lat}, Lon={new_lon}")

# Kalkış ve sürekli komut gönderme
try:
    arm_and_takeoff(10)  # 10 metreye kalk

    move_with_apf()
    

except KeyboardInterrupt:
    print("Görev iptal edildi.")
finally:
    print("İniş başlatılıyor...")
    vehicle.mode = VehicleMode("LAND")
    vehicle.close()
