import cv2
import time

# Örnek bir video kaynağı veya kamera kullanımı
video_source = 0  # 0 numaralı kamera (varsayılan)

# VideoCapture ile video akışı
cap = cv2.VideoCapture(video_source)

if not cap.isOpened():
    print("Kamera açılamadı!")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Görüntü alınamadı!")
        break

    # Zaman bilgisi
    current_time_ms = int(time.time() * 1000)
    time_text = f"Time: {current_time_ms} ms"

    # Dikdörtgenleri çizin (örnek koordinatlarla)
    height, width, _ = frame.shape
    cv2.rectangle(frame, (50, 50), (150, 150), (0, 255, 0), 2)  # Örnek dikdörtgen 1
    cv2.rectangle(frame, (width//2 - 50, height//2 - 50), 
                  (width//2 + 50, height//2 + 50), (255, 0, 0), 2)  # Örnek dikdörtgen 2

    # Zamanı görüntüye yazdırın
    cv2.putText(frame, time_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Görüntüyü göster
    cv2.imshow("Görüntü İşleme", frame)

    # 'q' tuşuna basıldığında çıkış yap
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kaynakları serbest bırak ve pencereleri kapat
cap.release()
cv2.destroyAllWindows()
