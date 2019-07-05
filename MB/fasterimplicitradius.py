from scipy.optimize import newton
from math import sqrt
import time

def GetRadius(Ri,DV,mu):

    def f(Rf):
        return sqrt(mu/Ri)*(sqrt(2*Rf/(Rf+Ri))-1)+sqrt(mu/Rf)*(1-sqrt(2*Ri/(Rf+Ri)))-DV

    return newton(f,Ri)

if __name__ == '__main__':
    starttime = time.time()
    print(GetRadius(6778000.,0.01,(398600.*10**9)))
    time = time.time()-starttime
    print(time)
