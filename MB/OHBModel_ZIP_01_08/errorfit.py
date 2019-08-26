from csvtodict import csvtodict
from curvefitter import csvtocurve
from csv import writer
from derivator import derivative
import matplotlib.pyplot as plt




times = [90,180,360]
dict = {}
for ttime in times:
    dictnew = csvtodict(f'Data/Output/RandMinput_errors{ttime}.csv')
    dict = {**dict,**dictnew}

lists = [[],[]]
newfile = writer(open('Data/Output/RandMinput_errors.csv','w+'))
for i in range(len(dict['Isp 90d Xdata'])):
    Isp = 0
    error = 0
    for days in times:
        Isp += dict[f'Isp {days}d Xdata'][i]
        error += dict[f'Isp {days}d Ydata'][i]
    Isp_average = Isp/3
    error_average = error/3
    lists[0].append(Isp_average)
    lists[1].append(error_average)
    newfile.writerow([Isp_average,error_average])



f = lambda x,a,b,c : a/(x**b)+c
func,popt = csvtocurve(f,'Data/Output/tester.csv',graph=True,givepopt=True)
print(popt)

data = derivative(lists[0],[func(i) for i in lists[0]],0.0001)
plt.plot(*data)
plt.show()
