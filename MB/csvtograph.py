from csv import reader
import matplotlib.pyplot as plt

def csvtodict(path,graph=False):
    datafile = list(reader(open(path)))
    names = []
    nlines = 0
    for data in datafile[0]:
        if data != '':
            nlines += 1
            names.append(data)
    #Remove First Rows Containing Names and X, Y
    del datafile[:2]
    #Transpose List to put data in rows
    datafile = list(zip(*datafile))
    datadict ={}
    #Removing Empty Strings
    for i,row in enumerate(datafile):
        datafile[i] = list(filter(lambda x:x!='',row))


    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.set_xlabel('Specific Impulse [s]')
    ax1.set_ylabel('Separation Mass [kg], Injection Height [km]')
    ax2.set_ylabel('Transfer Efficiency [%]')
    fig.suptitle('Soyuz OHB Data for several transfertimes')
    for i in range(0,len(datafile),2):
        #Turn String Data into Float
        Xdata = [float(i) for i in list(datafile[i])]
        Ydata = [float(i) for i in list(datafile[i+1])]

        iname = names[i//2]
        datadict[f'{iname} Xdata'] = Xdata
        datadict[f'{iname} Ydata'] = Ydata

        #Color, Name and Linetype Setting
        if '3' in path or '5' in path:
            if '90' in iname:
                linestyle = '-'
            if '180' in iname:
                linestyle = '--'
            if '360' in iname:
                linestyle = '-.'
            fig.suptitle('Soyuz OHB Data for several transfertimes')
            ncol = 1

        if '4' in path:
            if 'Soyuz' in iname:
                linestyle = '-'
            elif 'A62' in iname:
                linestyle = '--'
            elif 'A64' in iname:
                linestyle = '-.'
            else:
                linestyle = '-'
            # print(iname,linestyle)
            fig.suptitle('Comparison of MEO transfer for several launchers')
            ax1.set_ylim(top=16000)
            ax2.set_ylim(top=900)
            ncol = 7


        if 'Inject Height' in iname:
            color = 'g'
        else:
            color = 'k'
        if 'Trans. Eff.' in iname:
            name = f'{iname}'
            ax2.plot(Xdata,Ydata,label=name,color='darkorange',linestyle=linestyle)
        else:
            name = f'{iname}'
            ax1.plot(Xdata,Ydata,label=name,color=color,linestyle=linestyle)

    if graph == True:
        fig.legend(loc='upper left',bbox_to_anchor=(0.13,0.87),ncol=ncol)
        plt.show()
    return datadict

if __name__ == '__main__':
    print(csvtodict('Data/Fig5Wollenhaupt.csv',graph=True))
