from scipy.optimize import newton
from numpy import sqrt,arange
import matplotlib.pyplot as plt

def GetInitRadius(DV, Rf):
    mu = 398600
    def f(R0):
        return sqrt(mu/R0)*(sqrt(2*Rf/(Rf+R0))-1)+sqrt(mu/Rf)*(1-sqrt(2*R0/(Rf+R0)))-DV
    return newton(f,(Rf-10000.*DV))

DRlist = []
DVlist = list(range(100,300))
for i in DVlist:
    print(i)
    i = i/100.
    DRlist.append(GetInitRadius(i,23222))
plt.plot(DRlist,DVlist)
plt.show()
