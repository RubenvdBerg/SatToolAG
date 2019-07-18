from curvefitter import csvtocurve
from csv import reader
import matplotlib.pyplot as plt


path = 'Data/errordata.csv'
func = lambda x,a,b : a*x**b
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
print(R2,*popt)
print(str(func))
data, = plt.plot(datalist[0],datalist[1],'g')
curve, = plt.plot(datalist[0],datalist[2],'b')
data.set_label('Error Data')
curve.set_label('Curve Fit')
plt.legend()
plt.show()
