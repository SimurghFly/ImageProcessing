import numpy as np

def angle_between_vectors(v1, v2):
    dot_product = np.dot(v1, v2)  # Nokta çarpımı
    norm_v1 = np.linalg.norm(v1)  # Vektör 1'in büyüklüğü
    norm_v2 = np.linalg.norm(v2)  # Vektör 2'nin büyüklüğü
    cos_theta = dot_product / (norm_v1 * norm_v2)  # Kosinüs değeri

    angle_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))  # Radyan cinsinden açı
    angle_deg = np.degrees(angle_rad)  # Dereceye çevirme

    return angle_deg

def signed_angle(v1, v2):
    """
    İki 2D vektör arasındaki yönlü açıyı hesaplar.
    
    v1, v2: 2D vektörler (numpy array)
    """
    angle1 = np.arctan2(v1[1], v1[0])  # v1 vektörünün açısı
    angle2 = np.arctan2(v2[1], v2[0])  # v2 vektörünün açısı
    
    angle_deg = np.degrees(angle2 - angle1)  # İki açı arasındaki fark
    
    # Açıyı [-180, 180] aralığına getirme
    if angle_deg > 180:
        angle_deg -= 360
    elif angle_deg < -180:
        angle_deg += 360
    
    return angle_deg

# Hız ve konumdaki istenen değişimi alır
# Maxangle dan küçükse değişiklik yapmaz
# Maxangledan büyükse dönebileceği kadar döneceği şekilde yeni bir vektör verir
def normalize_move(v, next_move):
    max_angle = 45

    a = signed_angle(v, next_move)
    sign = 1 if a > 0 else -1
    rad = np.radians(max_angle*sign)
    if abs(a) > max_angle:
        next_move = np.array([np.cos(rad), np.sin(rad)])
    
    return next_move

def main():
    # Örnek kullanım
    v = np.array([-1, 0.3])
    next_move = np.array([0, 1])

    move = normalize_move(v, next_move)
    angle = signed_angle([0,0], move)
    print(f"Dönüş açısı {angle} derece.")

if __name__ == "__main__":
    main()