import numpy as np


def attractive(target, pos):
    att_k = 3

    force = target - pos
    d = pisagor(force, [0,0])
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

        d = pisagor(o_pos, pos) 

        if d < r:
            rep_force = rep_k * (pos - o_pos) / d
        elif d < 10*r: # It can be better to use r + d0 instead of 2r
            rep_force = rep_k * (pos - o_pos) * (1/d) * (1 / (d-r)**n)
            # rep_force = rep_k * (pos - o_pos) * r / d * 
        else: 
            rep_force = pos - pos # 0,0

        total_force = total_force + rep_force
    
    return total_force

# WE'LL NEED REPULSIVE FORCE FOR EDGES OF THE ZONE

def total(pos, target, obstacles, unity = True):
    t = repulsive(obstacles, pos) + attractive(target, pos)
    return t / ((t[0]**2 + t[1]**2)**0.5) if unity else t  # + duvarların ititci kuvveti

def pisagor(pos1, pos2):
    return ((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)**(0.5)

def test():
    target = np.array([10, 10])
    obstacles = [np.array([ [3,3], [2,0] ])]
    
    start_pos = np.array([2,2])

    a = total(start_pos, target, obstacles)

    print(a)

if __name__ == "__main__":
    test()