import time


class pidControl:
    def __init__(self, wanted, Ks = (1, 0, 0)):
        self.wanted = wanted
        self.Ks = Ks

        self.clear()


    def clear(self):
        self.lasterr = 0 # to diffreantiate and integrate
        self.A = 0 # For integral
        self.lasttime = time.perf_counter()


    def one_shot(self, val):
        temp = time.perf_counter()
        self.dt = (temp - self.lasttime)
        if not (self.dt > 0):
            self.dt = 0.001  
        self.lasttime = temp

        error = self.wanted - val
        self.A += self.dt * (self.lasterr + error) / 2

        p = error * self.Ks[0]
        i = self.A * self.Ks[1]
        d = ((error - self.lasterr) / self.dt  * self.Ks[2]) 

        u = p+i+d
        return u 

def main():
    dt = 0.1
    pid = pidControl(0, (1, 1, 1.8))
    
    val = 150
    for _ in range(50):
        control_signal = pid.one_shot(val)
        val += control_signal * pid.dt  # pid.dt çok küçük olursa zortluyor
        print(pid.A)
        # val += pid.dt * 700
        print(f"Control Signal: {control_signal:.2f}, Measurement: {val:.2f}")

if __name__ == "__main__":
    main()