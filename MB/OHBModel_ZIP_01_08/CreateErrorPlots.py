from csvtodict import csvtodict
from scipy.interpolate import interp1d
from csv import reader
import matplotlib.pyplot as plt
from FiguresDataCreate import create_fig3data, create_fig4data
import os


def fig3errorplot(path,inputR=False,inputM=False,erroronly=False,savefile=False,graph=False,range=(260,3600)):
    '''Turns data csv file created by create_fig3data into 3 error graphs that compares the model data with the orignal paper data'''
    create_fig3data(path,Isprange=range,step=20,inputR=inputR,inputM=inputM,graph=False)
    #Figure Number to plot
    fign = 3
    #Calling Original Data
    fig_dict, fig_names = csvtodict(f'Data/Fig{fign}Wollenhaupt.csv',give_names=True)

    #Opening Model data
    modelfile = reader(open(path))
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
    if erroronly == True:
        fig2, ax4 = plt.subplots()
        ax4.set_xlabel('Specific Impulse [s]')
        ax4.set_ylabel('Error [%]')
        ax5 = ax4.twinx()
        ax5.set_ylabel('Error[%] Injection Height')
        fig2.suptitle('Soyuz Multiple Transfer Time Errors')

        # ax4.set_xlim(left=0,right=4000)
        # ax4.set_ylim(top=15,bottom=-60)
        # ax5.set_ylim(top=600,bottom=-50)
    #Loop over the 3 transfer time options
    for days in [90,180,360]:
        if erroronly == False:
            #set-up the figure
            fig, ax1 = plt.subplots()
            fig.subplots_adjust(right=0.75)
            ax1.set_xlabel('Specific Impulse [s]')
            ax1.set_ylabel('Injection Height [km], Seperation Mass [kg]',)
            ax1.set_ylim(top=16000)
            ax2 = ax1.twinx()
            ax2.set_ylabel('Transfer Efficiency [%]')
            ax2.set_ylim(top=600)
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


            fig.suptitle(f'Soyuz MEO Transfer - Errors for {days} days transfer time{extra}')

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
        if erroronly == False:
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
        elif erroronly == True:
            errorlinestyledict = {'90':':','180':'-','360':'-.'}
            for i,label,errorcolor in zip(ilist,labels,errorcolors):
                if 'Height' in label:
                    ax5.plot(Isplist,errorlist[i],label=f'{label} Error {days} d',color=errorcolor,linestyle=errorlinestyledict[f'{days}'])
                else:
                    ax4.plot(Isplist,errorlist[i],label=f'{label} Error {days} d',color=errorcolor,linestyle=errorlinestyledict[f'{days}'])

    if erroronly == True:
        fig2.legend(loc='upper right',bbox_to_anchor= (.90,0.88))
        plt.show()

    if savefile == False:
        os.remove(path)

def fig4errorplot(path,inputR=False,inputM=False,erroronly=False,savefile=False,range=(260,3600)):
    create_fig4data(path,Isprange=range,step=20,inputR=inputR,inputM=inputM,graph=False)
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

    #Opening Model data
    modelfile = reader(open(path))

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

    if erroronly == True:
        fig2, ax4 = plt.subplots()
        ax4.set_xlabel('Specific Impulse [s]')
        # ax4.set_xlim(left=0,right=4000)0
        ax4.set_ylabel('Error [%]')
        # ax4.set_ylim(top=50,bottom=-25)
        fig2.suptitle('Multiple Launchers Errors')
    #Loop over the 3 launcher options
    for launchername in launchernames:
        if erroronly == False:
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
        if erroronly == False:
            #Plotting all Lines
            for i,label,color,errorcolor in zip(ilist,labels,colors,errorcolors):
                #Transfer Efficiency Plotted on different axis, because different order of magnitude than Mass and Height
                if 'Eff.' in label:
                    ax2.plot(Isplist,modellist[i],label=f'{label} Model',color=color,linestyle='--')
                    ax2.plot(Isplist,OGlist[i],label=f'{label} Original',color=color,linestyle='-')
                else:
                    ax1.plot(Isplist,modellist[i],label=f'{label} Model',color=color,linestyle='--')
                    ax1.plot(Isplist,OGlist[i],label=f'{label} Original',color=color,linestyle='-')

                #Errors for inject height irrelevant for this figure.
                if 'Height' not in label:
                    #Errors plotted on own axis as well because they can be negative
                    ax3.plot(Isplist,errorlist[i],label=f'{label} Error',color=errorcolor,linestyle=':')
                    #Form Legend and assign location
            fig.legend(loc='upper right',bbox_to_anchor= (.95,0.85))
            plt.show()
        elif erroronly == True:
            errorlinestyledict = {launchernames[0]:':',launchernames[1]:'-',launchernames[2]:'-.'}
            for i,label,errorcolor in zip(ilist,labels,errorcolors):
                ax4.plot(Isplist,errorlist[i],label=f'{label} Error {launchername}',color=errorcolor,linestyle=errorlinestyledict[f'{launchername}'])
    if erroronly == True:
        fig2.legend(loc='upper right',bbox_to_anchor= (.90,0.88))
        plt.show()
    if savefile == False:
        os.remove(path)


if __name__ == '__main__':
    fig3errorplot('Data/datatest.csv',inputR=False,inputM=False,erroronly=True)
