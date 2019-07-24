from OHBModel import OHBModel
from csv import writer
import matplotlib.pyplot as plt


if __name__ == '__main__':
    csvfile = writer(open('Data/soyuzdata.csv','w+'))
    linedict = {}
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Specific Impulse [s]')
    ax1.set_ylabel('Injection Height [km], Seperation Mass [kg]',)
    ax3 = ax1.twinx()
    ax3.set_ylabel('Transfer Efficiency [%]')
    ax3.set_ylim(top=600, bottom=0)
    fig.suptitle('Example MEO Transfer on an Soyuz - Model')

    for tdays,sign in [(90,'-'),(180,':'),(360,'--')]:

        # OHBModel(I_sp=1500., P_sat=5000.,t_trans=120*24*3600.,M_dry=2000.,R_f=15000.*10**3)
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
        linedict[f"lineS{tdays}"], = ax3.plot(Ilist,Slist,'r',linestyle=sign)

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
