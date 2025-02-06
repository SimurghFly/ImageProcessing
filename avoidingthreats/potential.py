import numpy as np

# Don't use this

ak = 1
rk = 500
rwk = 1

# Potansiyel Fonksiyon Tanımları
def attractive(x, y, target):
    return ak * ((x - target[0])**2 + (y - target[1])**2)
    return 0

def repulsive(x, y, obstacles, d0=3):
    obstacle = obstacles[0]
    r = obstacle[2]
    d = np.sqrt((x - obstacle[0])**2 + (y - obstacle[1])**2)

    d = np.maximum(d, 0.01)  # Sıfıra bölme hatasını önlemek için

    if d < r:
        return rk * (r-d) 
    elif d < d0:
        return rk * (1/d - 1/d0)**2
    else:
        return 0

def total(X, Y, j, i, target, obstacles):
    return attractive(X[j, i], Y[j, i], target) + repulsive(X[j, i], Y[j, i], obstacles)
