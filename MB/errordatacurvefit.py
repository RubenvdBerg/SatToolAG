from curvefitter import csvtocurve
from csv import reader
import matplotlib.pyplot as plt


path = 'Data/errordata.csv'
strfunc = 'a+b*x+c*x**2+d*x**3+e*x**4'
func = lambda x,a,b,c,d,e : eval(strfunc)
function, popt = csvtocurve(func,path,givepopt=True)

csvfile = reader(open(path))
datalist = [[],[],[]]
for i in csvfile:
    datalist[0].append(float(i[0]))
    datalist[1].append(float(i[1]))
    datalist[2].append(function(float(i[0])))


yaverage = sum(datalist[1])/len(datalist[1])
SStot = 0
SSres = 0
for y, f in zip(datalist[1],datalist[2]):
    SStot += (y-yaverage)**2
    SSres += (y-f)**2

R2 = 1-SSres/SStot
Ispstr = strfunc.replace('x','Isp')
print(f'The R2 factor is {R2}')
print(f'The function is {Ispstr}')
print(f'The factors are: a={popt[0]},b={popt[1]},c={popt[2]},d={popt[3]}')

fig, ax = plt.subplots()
data, = ax.plot(datalist[0],datalist[1],'g')
curve, = ax.plot(datalist[0],datalist[2],'b')
data.set_label('Absolute Error Data')
curve.set_label('Curve Fit')
ax.set_ylabel('Injection Height Error [km]')
ax.set_xlabel('Specific Impulse [s]')
fig.suptitle('Injection Height Error Curve')
textstr = '\n'.join((f'R2 = {R2:.5f}\n','Function:',f'{Ispstr}\n',f'a={popt[0]:.2E},  b={popt[1]:.2E}',f'c={popt[2]:.2E} ,   d={popt[3]:.2E}'))
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
fig.text(0.02, 0.02, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='bottom', bbox=props)
plt.legend()
plt.show()
