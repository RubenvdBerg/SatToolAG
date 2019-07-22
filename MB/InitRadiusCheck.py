from scipy.optimize import newton
from numpy import sqrt
import matplotlib.pyplot as plt

def GetInitRadius(DV, Rf):
    mu = 3.98600*10**14
    def f(R0):
        return sqrt(mu/R0)*(sqrt(2*Rf/(Rf+R0))-1)+sqrt(mu/Rf)*(1-sqrt(2*R0/(Rf+R0)))-DV
    return newton(f,Rf)

DVlist = []
DRlist = list(range(100,300))
for i in DRlist:
    DVlist.append(GetInitRadius(i,23222*10**3)/1000)
plt.plot(DRlist,DVlist)
plt.show()
