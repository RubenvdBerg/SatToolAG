from OHBModel import OHBModel
from csv import writer
import matplotlib.pyplot as plt


if __name__ == '__main__':
    #Open File to Write Data
    csvfile = writer(open('Data/soyuzdata.csv','w+'))

    #Set-Up plot 1
    linedict = {}
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Specific Impulse [s]')
    ax1.set_ylabel('Injection Height [km], Seperation Mass [kg]',)
    ax3 = ax1.twinx()
    ax3.set_ylabel('Transfer Efficiency [%]')
    ax3.set_ylim(top=600, bottom=0)
    fig.suptitle('Example MEO Transfer on an Soyuz - Model')

    #Loop over the 3 different transfertime cases
    for tdays,sign in [(90,'-'),(180,':'),(360,'--')]:

        Rlist = []
        Mlist = []
        Slist = []
        Ilist = []
        DVlist = []


        for i in range(200,3600,20):
            Ri, Mi, Si, DV = OHBModel(I_sp=i, P_sat=2500.,t_trans=tdays*24*3600.,M_dry=1000.,R_f=23222.*10**3,launcher='Soyuz')
            Rlist.append(Ri)
            Mlist.append(Mi)
            Slist.append(Si)
            Ilist.append(i)
            DVlist.append(DV)

        for Ri in Rlist:
            csvfile.writerow([Ri,Mi,Si])

        linedict[f"lineR{tdays}"], = ax1.plot(Ilist,Rlist,'g',linestyle=sign)
        linedict[f"lineM{tdays}"], = ax1.plot(Ilist,Mlist,'k',linestyle=sign)
        linedict[f"lineS{tdays}"], = ax3.plot(Ilist,Slist,'darkorange',linestyle=sign)

        linedict[f"lineR{tdays}"].set_label(f'Injection Height {tdays} days')
        linedict[f"lineM{tdays}"].set_label(f'Separation Mass {tdays} days')
        linedict[f"lineS{tdays}"].set_label(f'Transfer Efficiency {tdays} days')


    #Set Correct Legend Order
    legendlist = []
    for i,days in [(0,90),(1,180),(2,360)]:
        for a in ['R','M','S']:
            legendlist.append(linedict[f"line{a}{days}"])
    #Create Legends with ordered handles and give location
    fig.legend(handles=legendlist,loc='lower right',bbox_to_anchor=(0.88,0.11),ncol=3)
    plt.show()

    fig2, axx = plt.subplots()
    axx2 = axx.twinx()
    fig2dict = {}
    axx.set_xlabel('Specific Impulse [s]')
    axx.set_ylabel('Injection Height [km],Separation Mass[kg]')
    axx2.set_ylabel('Transfer Efficiency [%]')
    for launcher, sign2 in [('Ariane62','--'),('Ariane64',':'),('Soyuz','-')]:
        datalist = [[],[],[]]
        Ilist2 = []
        for Isp in range(200,3600,20):
            Ri, Mi, Si, DV = OHBModel(I_sp=Isp, P_sat=2500.,t_trans=90*24*3600.,M_dry=1000.,R_f=23222.*10**3,launcher=launcher)
            datalist[0].append(Ri)
            datalist[1].append(Mi)
            datalist[2].append(Si)
            Ilist2.append(Isp)
        fig2dict[f'Sline{launcher}'], = axx2.plot(Ilist2,datalist[2], linestyle=sign2,color='darkorange',label=f'Transfer Efficiency {launcher}')
        fig2dict[f'Mline{launcher}'], = axx.plot(Ilist2,datalist[1], linestyle=sign2,color='k',label=f'Separation Mass {launcher}')
    Rline, = axx.plot(Ilist2,datalist[0],'g',label='Injection Height')

    handles2 = [Rline,fig2dict['SlineAriane62'],fig2dict['SlineAriane64'],fig2dict['SlineSoyuz'],fig2dict['MlineAriane62'],fig2dict['MlineAriane64'],fig2dict['MlineSoyuz']]

    fig2.legend(handles=handles2,loc='upper right',bbox_to_anchor=(0.88,0.88),ncol=2)
    fig2.suptitle('Comparison of Different Launchers - Model')
    plt.show()
