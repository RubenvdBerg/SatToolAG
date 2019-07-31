from csvtodict import csvtodict
from scipy.interpolate import interp1d
from csv import reader
import matplotlib.pyplot as plt

#Figure Number to plot
fign = 3
#Calling Original Data
fig_dict, fig_names = csvtodict(f'Data/Fig{fign}Wollenhaupt.csv',give_names=True)
print(f'Figure names are:{fig_names}')

#Opening Model data
modelfile = reader(open('Data/soyuzdata.csv'))
# fig4modelfile = reader(open('Data/launcherdata.csv'))

#Interpolating Original Data to interpolated curve functions in a dictionary
funcdict = {}
for fig_name in fig_names:
    funcdict[f'{fig_name}'] = interp1d(fig_dict[f'{fig_name} Xdata'],fig_dict[f'{fig_name} Ydata'])

#Turning modelfile into a dictionary with all relevant data
#(bit annoying because the modelfile has different transfer times below eachother instead of different columns)
counter = 45
modeldict = {}
for row in modelfile:
    if 'Isp' in row[0]:
        counter *=2
        datalist = []
    else:
        Isp  = float(row[0])
        Rinj = float(row[1])
        Msep = float(row[2])
        Teff = float(row[3])
        datalist.append([Isp, Rinj, Msep, Teff])
        modeldict[f'{counter}days'] = datalist

#Loop over the 3 transfer time options
for days in [90,180,360]:
    #set-up the figure
    fig, ax1 = plt.subplots()
    fig.subplots_adjust(right=0.75)
    ax1.set_xlabel('Specific Impulse [s]')
    ax1.set_ylabel('Injection Height [km], Seperation Mass [kg]',)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Transfer Efficiency [%]')
    ax2.set_ylim(top=600)
    ax3 = ax1.twinx()
    ax3.set_ylabel('Error [%]')
    fig.suptitle(f'Soyuz MEO Transfer - Errors for {days} days transfer time')

    #set-up separate third axis
    def make_patch_spines_invisible(ax):
        ax.set_frame_on(True)
        ax.patch.set_visible(False)
        for sp in ax.spines.values():
            sp.set_visible(False)
    ax3.spines['right'].set_position(('axes',1.08))
    make_patch_spines_invisible(ax3)
    ax3.spines['right'].set_visible(True)


    #Main data Loop
    Isplist = []
    #List will all be [0]=Inject Height,[1]=Separation Mass,[2]=Transfer Efficiency
    modellist = [[],[],[]]
    OGlist = [[],[],[]]
    errorlist = [[],[],[]]
    for data in modeldict[f'{days}days']:
            #Assigning Correct Values
            Isp     = float(data[0])
            Rinj    = float(data[1])
            Msep    = float(data[2])
            Teff    = float(data[3])
            #Assigning the previously interpolated functions
            Rfunc   = funcdict[f'Inject Height {days} d']
            Mfunc   = funcdict[f'Sep. Mass {days} d']
            Sfunc   = funcdict[f'Trans. Eff. {days} d']

            #Setting up iterables
            variables   = [Rinj, Msep, Teff]
            ilist       = [0,1,2]
            functions   = [Rfunc,Mfunc,Sfunc]
            #Append Values to the right lists
            for variable,i,func in zip(variables,ilist,functions):
                modellist[i].append(variable)
                OGlist[i].append(func(Isp))
                errorlist[i].append((variable-func(Isp))/func(Isp)*100.)
            Isplist.append(Isp)
    #Setting up iterables
    colors      = ['g','k','orange']
    labels      = ['Inject Height','Sep. Mass','Trans. Eff.']
    errorcolors = ['darkgreen','k','darkorange']
    #Plotting all Lines
    for i,label,color,errorcolor in zip(ilist,labels,colors,errorcolors):
        #Transfer Efficiency Plotted on different axis, because different order of magnitude than Mass and Height
        if 'Eff.' in label:
            ax2.plot(Isplist,modellist[i],label=f'{label} Model',color=color,linestyle='--')
            ax2.plot(Isplist,OGlist[i],label=f'{label} Original',color=color,linestyle='-')
        else:
            ax1.plot(Isplist,modellist[i],label=f'{label} Model',color=color,linestyle='--')
            ax1.plot(Isplist,OGlist[i],label=f'{label} Original',color=color,linestyle='-')
        #Errors plotted on own axis as well because they can be negative
        ax3.plot(Isplist,errorlist[i],label=f'{label} Error',color=errorcolor,linestyle=':')
    #Form Legend and assign location
    fig.legend(loc='upper right',bbox_to_anchor= (.95,0.85))
    plt.show()
