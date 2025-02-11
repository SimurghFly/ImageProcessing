import numpy as np
import matplotlib.pyplot as plt
import force

def main():
    pos = np.array([9, 9])
    target = np.array([6,4])
    obstacles = [
        np.array([[5,5],[1,0]]),
        np.array([[7,10],[2,0]]),
    ]

    x_range = np.linspace(0, 18, 20)
    y_range = np.linspace(0, 18, 20)
    X, Y = np.meshgrid(x_range, y_range)

    U = np.zeros_like(X)
    V = np.zeros_like(Y)

    for i in range(len(x_range)):
        for j in range(len(y_range)):
            force_vec = force.total(np.array([X[j, i], Y[j, i]]), target, obstacles)
            U[j, i] = force_vec[0]
            V[j, i] = force_vec[1]

    plt.figure(figsize=(8,8))
    plt.xlim(0, 18)
    plt.ylim(0, 18)
    plt.gca().set_aspect('equal', adjustable='box')
    
    plt.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1, color='blue')
    plt.scatter(target[0], target[1], color='green', label='Target')
    plt.scatter(pos[0], pos[1], color='black', label='Start Position')
    
    for obs in obstacles:
        center = obs[0]
        radius = obs[1][0]
        circle = plt.Circle(center, radius, color='red', fill=False)
        plt.gca().add_patch(circle)
    
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Vector Field Visualization")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    main()
