from OHBModel import OHBModel
from csv import reader, writer, QUOTE_MINIMAL
from numpy import array
import matplotlib.pyplot as plt


radiusdata = reader(open('Data/InjectHeight.csv'))
Isp = []
ROHBlist = []
Rmodel = []
difference = []
error = []
for i in radiusdata:
    Isp.append(float(i[0]))
    ROHB = float(i[1])
    ROHBlist.append(ROHB)
    R, Msep, SatR, DV = OHBModel(I_sp=float(i[0]), P_sat=5000.,t_trans=120*24*3600.,M_dry=2000.,R_f=23222.*10**3)
    Rmodel.append(R)
    difference.append((R-ROHB)/ROHB*100)
    error.append(R-ROHB)

file = open('Data/errordata.csv', 'w+')
csvfile = writer(file,delimiter=',',quotechar='"',quoting=QUOTE_MINIMAL)
for i in error:
    i = str(i)
for i in Isp:
    i = str(i)
list = [Isp,error]
for i in zip(*list):
    csvfile.writerow(i)
# print(f'Isp {Isp}')
# print(f'ROHB {ROHBlist}')
# print(f'R {Rmodel}')
fig, ax1 = plt.subplots()
fig.suptitle('Comparison Model and Data of OHB paper')
line1, = ax1.plot(Isp,ROHBlist,'b')
line2, = ax1.plot(Isp,Rmodel,'c')
line4, = ax1.plot(Isp,error,'r')
ax1.set_ylabel('Injection Height [km]')
ax1.set_xlabel('Specific Impulse [s]')
line1.set_label('OHB Values')
line2.set_label('Model Values')
line4.set_label('Absolute Error')


ax2 = ax1.twinx()

line3, = ax2.plot(Isp,difference,'tab:orange')
ax2.set_ylabel('Difference [%]')
line3.set_label('Difference %')
fig.legend(loc='upper left',bbox_to_anchor=(0.6,0.5))
plt.show()
