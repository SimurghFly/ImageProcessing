import math
from pid import pidControl

class PIDControl3d:
    def __init__(self, wanted, Ks ):

        # wanted is a list, yaw için targetın istenen x i, 
        # pitch için targetın istenen y si, 
        # distance içinse targetın istenen büyüklüğü (ekrana göre yüzdelik)
        self.target = wanted

        # Ks katsayıları tutuyor gerekirse üç kontrolcü için farklı katsayılar kullanırız
        self.Ks = Ks


        self.yawPidControl = pidControl(wanted[0], Ks)
        self.pitchPidControl = pidControl(wanted[1], Ks)
        self.distancePidControl = pidControl(wanted[2], Ks)

        self.clear()

    def clear(self):
        self.yawPidControl.clear()
        self.pitchPidControl.clear()
        self.distancePidControl.clear()

    def one_shot(self, target):
        uyaw = self.yawPidControl.one_shot(target[0])
        upitch = self.pitchPidControl.one_shot(target[1])
        udistance = self.distancePidControl.one_shot(target[2])

        # yawangle = arctan( uyaw * tanQ / 50 ) ve belki * self.yawPidControl.dt 
        # Q is half of the horizantal pov of the camera
        yawangle = math.atan(uyaw * (0.7673) / 50) # 0.7673 = tan37,5

        # pitchangle = arctan( upitch * tanP / 50 ) ve belki * self.pitchPidControl.dt 
        # P is half of the vertical pov of the camera
        pitchangle = math.atan(upitch * (0.57735) / 50) # # 0.57735 = tan30

        # newvelocity = udistance * blabla


        return yawangle, pitchangle # , newvelocity


def main():
    def changeTarget(target, yawangle, pitchangle):
        target[0] += yawangle
        target[1] += pitchangle

    ctrl = PIDControl3d((0,0,20), (1,0,0))

    target = [10,10,5] # Hedefimiz burdaymışmış

    for _ in range(150):
        yawangle, pitchangle = ctrl.one_shot(target)

        # turn(yawangle)
        # turn(pitchangle)
        # Bu noktada bu açıların uçağa zara verecek şekilde olması mümkün,
        # Koruma kodunu turn fonksiyonuna saklamak lazım
        # Gerekirse turn hata döndürecek ve biz de hatayı yakalayıp takibi sonlandıracağız

        # Hızlanıp yavaşlama kodu da gerekebilir, onu nasıl yaparız bakmak lazım

        changeTarget(target, yawangle, pitchangle)
        print(target)

    
         
if __name__ == "__main__":
    main()