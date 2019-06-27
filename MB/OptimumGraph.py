from MBCalcFunc import MBatteryCalc, MSolarCalc
import matplotlib.pyplot as plt

tlist = []
for M_b in range(1,88):
    tlist.append(MBatteryCalc(M_b)/3600.)

plt.plot(range(1,88), tlist)
plt.ylabel('Total Maneuvre Time [h]')
plt.xlabel('Battery Mass [kg]')
plt.show()


tlist = []
for M_sa in range(1,88):
    tlist.append(MSolarCalc(M_sa)/3600.)

plt.plot(range(1,88), tlist)
plt.ylabel('Total Maneuvre Time [h]')
plt.xlabel('Solar Mass [kg]')
plt.show()
