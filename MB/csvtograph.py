from csv import reader
import matplotlib.pyplot as plt

def csvtograph(path):
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
    for i in range(0,len(datafile),2):
        #Turn String Data into Float
        Xdata = [float(i) for i in list(datafile[i])]
        Ydata = [float(i) for i in list(datafile[i+1])]
        datadict[f'Xdata{names[i//2]}'] = Xdata
        datadict[f'Ydata{names[i//2]}'] = Ydata
        # plt.subplot(1,nlines,i//2+1)
        # plt.ylim(bottom=0)
        # plt.xlim(left=0)

        if 'IH' in names[i//2]:
            color = 'g'
        else:
            color = 'k'
        if 'TE' in names[i//2]:
            name = f'{names[i//2]}'
            ax2.plot(Xdata,Ydata,label=name,color='darkorange')
        else:
            name = f'{names[i//2]}'
            ax1.plot(Xdata,Ydata,label=name,color=color)

    fig.legend()
    plt.show()
    # for i in range(nlines):
    #     x =1


if __name__ == '__main__':
    csvtograph('Data/Fig3Wollenhaupt2.csv')
