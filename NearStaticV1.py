from math import sqrt
import numpy as np
import matplotlib.pylab as plt

#Continuous Inputs
Mps = 50.
Mu = 50.
M0 = 150.
R0 = 6.778*10**6
Rf = 7.578*10**6
Esp = 3600.*65
Ft = 0.015
ve = 9810
Pft = 250
Psk = 100
Zsa = 2.8
ndegr = 0.85
nsa = 0.375
ndis = 0.85
#Constants
Gsc = 1361
mu = 3.986*10**14

#Explicit Direct Equations
DVt = sqrt(mu/R0)*(sqrt(2*Rf/(R0+Rf))-1) + sqrt(mu/Rf)*(1-sqrt(2*R0/(R0+Rf)))
Mp = M0*(1-np.exp(-DVt/ve))
Asa = Psk/(Gsc*nsa*ndegr)
Msa = Zsa*Asa
Psa = Asa*Gsc*nsa
Mbatt = M0 -(Mp+Msa+Mu+Mps)
Cbatt = Mbatt*Esp
Tch = Cbatt/(Psa-Psk)
Tth = Cbatt*ndis/(Pft - (Psa-Psk))
Tcy = Tch + Tth

#Iterative Equations and Plotting
Mi = M0
i = 0            #cycle counterprint(f"The Propellant Mass will be {Mp} kg of Xenon")
DVtot = 0        #state DV
DVtlist =[]      #state DV list
DV = []          #DV list
M = []           #state M list
while DVtot < DVt:
    #Calculations
    DVi = Ft/Mi*Tth
    DVtot += DVi

    #plotlists
    DVtlist.append(DVtot)
    DV.append(DVi)
    M.append(Mi)

    #Resume Calc.
    Mi = np.exp(-DVi/ve)*Mi
    i += 1

ic = i-(1-(DVtot-DVt)/DVi) #linear assumed correction for overshooting the Total DV

#Data Overview
print("Orbit Transfer requires a "+u"Δ"+f"V of {DVt:.2f} m/s ")
print(f"Orbit Tranfer commenced in {ic:.2f} cycles")
print(f'The Transfer Time is {(ic*Tcy)/3600/24:.2f} days')
print(f'A Thrust Phase lasts {Tth/3600:.2f} hours')
print(f"A Charging Phase lasts {Tch/3600:.2f} hours")
print(f"The Solar Array will be {Asa:.2f} square meters")
print(f"The Battery will weigh {Mbatt:.2f} kg")
print(f"The Battery will have a capacity of {Cbatt:.0f} Joules or {Cbatt/3600:.0f} Wh")
print(f"The Propellant Mass will be {Mp:.2f} kg of Xenon")

#Plotstuff
ilist = list(range(i))
fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('time (s)')
ax1.set_ylabel('Mass')
ax1.plot(ilist, M, color='tab:red')
ax1.tick_params(axis='y', labelcolor='tab:red')

ax2 = ax1.twinx()

ax2.set_ylabel('Delta V')
ax2.plot(ilist, DVtlist, color='tab:blue')
ax2.tick_params(axis='y', labelcolor='tab:blue')
fig.tight_layout()
plt.show()
