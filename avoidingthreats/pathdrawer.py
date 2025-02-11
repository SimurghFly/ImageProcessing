import numpy as np
import matplotlib.pyplot as plt
import force

def main():
    # Tum konumlar ve yarıcaplar kucultulecek
    # Kucultme oranı (t*v den büyük bir oran)

    target = np.array([1,1])

    obstacles = [
        np.array([[12,7],[1,0]]),
        np.array([[5,11],[2,0]]),
    ]

    pos = np.array([15, 10])
    lastpos = pos

    # draw a green point at target
    # draw a black point at pos
    # draw a red daire for obstacles  5 5 konum, 2 r
    plt.figure()
    plt.xlim(0, 18)
    plt.ylim(0, 18)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Pathfinding Visualization")
    
    draw_target(target)
    draw_obstacles(obstacles)
    draw_position(pos)
    plt.legend()
    plt.ion()
    plt.show()
    
    try:
        while force.pisagor(pos, target) > 1:
            f = force.total(pos, target, obstacles)
            lastpos = pos
            pos = pos + f * 2
            #draw a line between pos and lastpos
            draw_path(lastpos, pos)
            # burda çiz demek yerine şu konuma git diyeceğiz 
            # !!!!!!! eğer çok büyük bir açıyla manevra ettirmek istersek açıyı küçükltmeliyiz
            plt.scatter(pos[0], pos[1], color='black')
            plt.pause(0.1)
    finally:
        plt.ioff()
        plt.show()

    print("bitti")

def draw_target(target):
    plt.scatter(target[0], target[1], color='green', label='Target')

def draw_obstacles(obstacles):
    for obs in obstacles:
        center = obs[0]
        radius = obs[1][0]
        circle = plt.Circle(center, radius, color='red', fill=False)
        plt.gca().add_patch(circle)

def draw_position(pos):
    plt.scatter(pos[0], pos[1], color='black', label='Position')

def draw_path(lastpos, pos):
    plt.plot([lastpos[0], pos[0]], [lastpos[1], pos[1]], color='blue')


if __name__ == "__main__":
    main()