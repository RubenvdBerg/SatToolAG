import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from FiguresDataCreate import create_fig3data
import matplotlib.pyplot as plt
import time

start_time = time.time()
path = 'Data/Output/fig3data.csv'
start,stop,step = 250,3850,5
create_fig3data(path,Isprange=(start,stop),step=step,graph=False)

pdf = pd.read_csv(path,header=None)
loc180 = pdf.loc[pdf[0]=='Isp 180'].index[0]
loc360 = pdf.loc[pdf[0]=='Isp 360'].index[0]
pdf90 = pdf.iloc[:loc180].reset_index(drop=True)
pdf180 = pdf.iloc[loc180:loc360].reset_index(drop=True)
pdf360 = pdf.iloc[loc360:].reset_index(drop=True)
modelpd = pd.concat([pdf90,pdf180,pdf360],axis=1,ignore_index=True)

datapath = 'Data/Fig3Wollenhaupt.csv'
datapd = pd.read_csv(datapath,header=None)
funcdict = {}
valdict = {}
vals = []

# print(datapd)
names = datapd.loc[0]
for i,name in enumerate(names):
    if not pd.isnull(name):
        x = datapd[i].iloc[2:]
        y = datapd[i+1].iloc[2:]
        def lister(i):
            i = i.values.tolist()
            i = [float(j) for j in i if str(j)!='nan']
            return i

        x = lister(x)
        y = lister(y)
#         print(f'Bounds for {name} are {x[0]} and {x[-1]}')
        func = funcdict[name] = interp1d(x,y)

        func = funcdict[name]
        vallist = [float(func(Isp)) for Isp in np.arange(start,stop,step)]
        vals.append(vallist)
vals = np.array(vals)

modelpd = modelpd.drop(columns=[0,4,8])
modelpd = modelpd.drop([0],axis=0)
modelpd = modelpd.reindex(columns=[11,7,3,10,6,2,9,5,1])
mvals = modelpd.to_numpy('float')
mvals = mvals.T
errors = (mvals-vals)/vals*100





xlist = np.arange(start,stop,step)
datas = [vals,mvals,errors]
derivs = {}
names = ['vals','mvals','errors']
def deriv(y,x):
    return np.diff(y)/np.diff(x)

for i,data in enumerate(datas):
    derivs[names[i]] = [deriv(row,xlist) for row in data]
# valsinfl = [[],[],[]]
# for i in range(3):
#     for dTE in derivs['vals'][i]:
#         if -x<=dTE<x:
#             valsinfl[i].append(dTE)
# print(valsinfl)
elapsed_time = time.time() - start_time
print(elapsed_time)

#Set-Up Plot
fig, ax1 = plt.subplots()
ax1.set_xlabel('Specific Impulse [s]')
ax1.set_ylabel('Inject Height [km],Sep. Mass [kg]')
ax2 = ax1.twinx()
ax2.set_ylabel('Transfer Efficiency [%]')
fig.suptitle('Errors for Figure 3 Data')

for i,values in enumerate(errors):
    if i in [0,3,6]:
        linestyle = ':'
        label= '360d'
    elif i in [1,4,7]:
        linestyle = '-.'
        label = '180d'
    else:
        label = '90d'
    if i < 3:
        ax2.plot(xlist,values,color='darkorange',linestyle=linestyle, label=f'Trans. Eff. {label}')
    elif i < 6:
         ax1.plot(xlist,values,color='k',linestyle=linestyle,label=f'Sep. Mass {label}')
    else:
        ax1.plot(xlist,values,color='g',linestyle=linestyle,label=f'Inject. Height {label}')

fig.legend()
plt.show()

fig2, ax3 = plt.subplots()
ax3.set_xlabel('Specific Impulse [s]')
ax3.set_ylabel('Inject. Height Derivatives',color='g')
fig2.suptitle('Derivatives of Figure 3 Data_Errors')
ax32 = ax3.twinx()
ax32.set_ylabel('Trans. Eff., Sep. Mass Derivatives')
x2list = xlist[:-1]
for i,values in enumerate(derivs['errors']):
    if i in [0,3,6]:
        linestyle = ':'
        label= '360d'
    elif i in [1,4,7]:
        linestyle = '-.'
        label = '180d'
    else:
        label = '90d'
        linestyle = '-'
    if i < 3:
        ax32.plot(x2list,values,color='darkorange',linestyle=linestyle, label=f'Trans. Eff. {label}')
    elif i < 6:
         ax32.plot(x2list,values,color='k',linestyle=linestyle,label=f'Sep. Mass {label}')
    else:
        ax3.plot(x2list,values,color='g',linestyle=linestyle,label=f'Inject. Height {label}')

fig2.legend()
plt.show()


fig3,ax4 = plt.subplots()
ax4.set_xlabel('Specific Impulse [s]')
ax4.set_ylabel('Inject. Height, Sep. Mass Derivatives')
ax42 = ax4.twinx()
ax42.set_ylabel('Trans. Eff. Derivatives',color='darkorange')
fig3.suptitle('Derivatives of Figure 3 Model Data')
for i,values in enumerate(derivs['mvals']):
    if i in [0,3,6]:
        linestyle = ':'
        label= '360d'
    elif i in [1,4,7]:
        linestyle = '-.'
        label = '180d'
    else:
        label = '90d'
        linestyle = '-'
    if i < 3:
        ax42.plot(x2list,values,color='darkorange',linestyle=linestyle, label=f'Trans. Eff. {label}')
    elif i < 6:
         ax4.plot(x2list,values,color='k',linestyle=linestyle,label=f'Sep. Mass {label}')
    else:
        ax4.plot(x2list,values,color='g',linestyle=linestyle,label=f'Inject. Height {label}')

fig3.legend()
plt.show()


fig4,ax5 = plt.subplots()
ax5.set_xlabel('Specific Impulse [s]')
ax5.set_ylabel('Inject. Height, Sep. Mass Derivatives')
ax52 = ax5.twinx()
ax52.set_ylabel('Trans. Eff. Derivatives',color='darkorange')
fig4.suptitle('Derivatives of Figure 3 Original Data')
for i,values in enumerate(derivs['vals']):
    if i in [0,3,6]:
        linestyle = ':'
        label= '360d'
    elif i in [1,4,7]:
        linestyle = '-.'
        label = '180d'
    else:
        label = '90d'
        linestyle = '-'
    if i < 3:
        ax52.plot(x2list,values,color='darkorange',linestyle=linestyle, label=f'Trans. Eff. {label}')
    elif i < 6:
         ax5.plot(x2list,values,color='k',linestyle=linestyle,label=f'Sep. Mass {label}')
    else:
        ax5.plot(x2list,values,color='g',linestyle=linestyle,label=f'Inject. Height {label}')

fig4.legend()
plt.show()
