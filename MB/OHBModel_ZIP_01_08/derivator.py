from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from FiguresDataCreate import create_fig3data,create_fig4data
from csvtodict import csvtodict
from csv import reader

def derivative(xlist,ylist,h):
    #Interpolate the data to a function
    y = interp1d(xlist,ylist)
    #Remove last element to stay within interpolation range
    x1list = xlist[:-1]
    x2list = [x+h for x in x1list]
    yderivlist = [
        (y(x2)-y(x1))/h
        for x1, x2 in zip(x1list,x2list)
    ]
    return x1list,yderivlist

path3 = 'Data/Output/Fig3_Derivate.csv'
create_fig3data(path3,graph=False)
errorfile = reader(open(path3))
errorfile = list(errorfile)
datalist = [[] for i in errorfile[0]]
dict = {}
for row in errorfile:
    try:
        for i in range(len(row)):
            datalist[i].append(float(row[i]))
    except ValueError:
        if datalist[0] != []:
            for i in range(len(names)):
                dict = {**dict, names[i]:datalist[i]}
            datalist = [[] for i in errorfile[0]]
        names = []
        for i in range(len(row)):
            names.append(row[i])
ddict = {}
for i in range(len(names)):
    dict = {**dict, names[i]:datalist[i]}
for key in dict.keys():
    if not 'Isp' in key:
        ddict[f'derivate{key}'] = derivative(dict['Isp 90'],dict[key],0.00001)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.set_ylabel('Inject Height[km],Sep. Mass [kg]')
ax2.set_ylabel('Trans. Eff. [%]')
ax1.set_xlabel('Specific Impulse [s]')
fig.suptitle('Derivatives Figure 3')
print(ddict.keys())
for key in ddict.keys():
    if '90' in key:
        linestyle = '-'
    if '180' in key:
        linestyle = ':'
    if '360' in key:
        linestyle = '-.'
    if 'Height' in key:
        color = 'g'
    if 'Mass' in key:
        color = 'k'
    if 'Eff' in key:
        color = 'darkorange'
        ax2.plot(*ddict[key],color=color,linestyle=linestyle,label=key)
    else:
        ax1.plot(*ddict[key],color=color,linestyle=linestyle,label=key)
fig.legend()
plt.show()
