from csvtodict import csvtodict
from scipy.interpolate import interp1d
from csv import reader
import matplotlib.pyplot as plt
from FiguresDataCreate import create_fig4data

def fig4errorplot(path,inputR=False,inputM=False):
    create_fig4data(path,Isprange=(260,3600),step=20,inputR=inputR,inputM=inputM)
    #Figure Number to plot
    fign = 4
    #Calling Original Data
    fig_dict, fig_names = csvtodict(f'Data/Fig{fign}Wollenhaupt.csv',give_names=True)
    # print(f'Figure names are:{fig_names}')

    #Opening Model data
    modelfile = reader(open(path))


    #Interpolating Original Data to interpolated curve functions in a dictionary
    funcdict = {}
    for fig_name in fig_names:
        funcdict[f'{fig_name}'] = interp1d(fig_dict[f'{fig_name} Xdata'],fig_dict[f'{fig_name} Ydata'])


    #Figure Number to plot
    fign = 4
    #Calling Original Data
    fig_dict, fig_names = csvtodict(f'Data/Fig{fign}Wollenhaupt.csv',give_names=True)
    print(f'Figure names are:{fig_names}')

    #Opening Model data
    modelfile = reader(open('Data/fig4datatest.csv'))

    #Interpolating Original Data to interpolated curve functions in a dictionary
    funcdict = {}
    for fig_name in fig_names:
        funcdict[f'{fig_name}'] = interp1d(fig_dict[f'{fig_name} Xdata'],fig_dict[f'{fig_name} Ydata'])

    launchernames = ['Ariane62','Ariane64','Soyuz']
    #Turning modelfile into a dictionary with all relevant data
    #(bit annoying because the modelfile has different launchers below eachother instead of different columns)
    counter = -1
    modeldict = {}
    for row in modelfile:
        if 'Isp' in row[0]:
            counter +=1
            datalist = []
        else:
            Isp  = float(row[0])
            Rinj = float(row[1])
            Msep = float(row[2])
            Teff = float(row[3])
            datalist.append([Isp, Rinj, Msep, Teff])
            modeldict[f'{launchernames[counter]}'] = datalist

    #Loop over the 3 launcher options
    for launchername in launchernames:
        #set-up the figure
        fig, ax1 = plt.subplots()
        fig.subplots_adjust(right=0.75)
        ax1.set_xlabel('Specific Impulse [s]')
        ax1.set_ylabel('Injection Height [km], Seperation Mass [kg]')
        ax1.set_ylim(top=16000)
        ax2 = ax1.twinx()
        ax2.set_ylabel('Transfer Efficiency [%]')
        ax2.set_ylim(top=900)
        ax3 = ax1.twinx()
        ax3.set_ylabel('Error [%]')
        if inputR == True and inputM == True:
            extra = ' for original R_inj and M_sep'
        elif inputR == True:
            extra = ' for original R_inj'
        elif inputM == True:
            extra = ' for original M_sep'
        else:
            extra = ''
        fig.suptitle(f'MEO Transfer - Errors for {launchername} {extra}')

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
        for data in modeldict[f'{launchername}']:
                #Assigning Correct Values
                Isp     = float(data[0])
                Rinj    = float(data[1])
                Msep    = float(data[2])
                Teff    = float(data[3])
                #Assigning the previously interpolated functions (only one inject height, same for all launchers)
                Rfunc   = funcdict[f'Inject Height']
                Mfunc   = funcdict[f'Sep. Mass {launchername}']
                Sfunc   = funcdict[f'Trans. Eff. {launchername}']

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
            if 'Height' not in label:
                #Errors plotted on own axis as well because they can be negative
                ax3.plot(Isplist,errorlist[i],label=f'{label} Error',color=errorcolor,linestyle=':')
        #Form Legend and assign location
        fig.legend(loc='upper right',bbox_to_anchor= (.95,0.85))
        plt.show()

if __name__ == '__main__':
    fig4errorplot('Data/fig4errorplottestfile.csv',inputR=False,inputM=True)
