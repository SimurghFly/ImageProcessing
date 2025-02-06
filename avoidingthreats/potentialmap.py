import numpy as np
import matplotlib.pyplot as plt

import potential

#Don't use this

# Grid oluştur
x_range = np.linspace(-10, 10, 20)
y_range = np.linspace(-10, 10, 20)
X, Y = np.meshgrid(x_range, y_range)

# Hedef ve engel tanımla
target = np.array([5, 5])
obstacles = [np.array([-3, -3, 1])]
obstacle = obstacles[0]

# Toplam Potansiyeli Hesapla
U = np.zeros_like(X)
for i in range(len(x_range)):
    for j in range(len(y_range)):
        U[j, i] = potential.total(X, Y, j, i, target, obstacles)

# Potansiyel alanın gradyanını hesapla (vektör yönleri)
dUx, dUy = np.gradient(-U)

# Vektör alanını normalize et
magnitude = np.sqrt(dUx**2 + dUy**2)  # Her vektörün büyüklüğünü hesapla
magnitude[magnitude == 0] = 1  # Sıfır bölme hatasını önlemek için

# Sabit uzunlukta vektörler oluştur
dUx_normalized = dUx / magnitude
dUy_normalized = dUy / magnitude

# Görselleştirme
plt.figure(figsize=(8, 8))
plt.contourf(X, Y, U, levels=50, cmap="coolwarm")  # Potansiyel alanı kontur olarak çiz
plt.colorbar(label="Potansiyel Değeri")

# Vektör alanını çiz
plt.quiver(X, Y, dUx_normalized, dUy_normalized, color="black", scale=50)

# Hedef ve engeli işaretle
plt.scatter(*target, color="green", s=100, label="Hedef")
plt.scatter(obstacle[0], obstacle[1], color="red", s=100, label="Engel")

plt.xlabel("X Konumu")
plt.ylabel("Y Konumu")
plt.title("Yapay Potansiyel Alan ve Vektörler")
plt.legend()
plt.show()
