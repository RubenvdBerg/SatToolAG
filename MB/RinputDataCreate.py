from OHBModel import OHBModel
from csv import writer
import matplotlib.pyplot as plt
from csvtodict import csvtodict
from scipy.interpolate import interp1d


if __name__ == '__main__':
    #Open File to Write Data
    path = 'Data/soyuzdataRinput.csv'
    csvwrite = writer(open(path,'w+'))
    #Set-Up plot 1
    linedict = {}
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Specific Impulse [s]')
    ax1.set_ylabel('Injection Height [km], Seperation Mass [kg]',)
    ax3 = ax1.twinx()
    ax3.set_ylabel('Transfer Efficiency [%]')
    ax3.set_ylim(top=600, bottom=0)
    fig.suptitle('Example MEO Transfer on an Soyuz - Model')

    #Loading Original Data to use the injection height input.
    OGdatapath = 'Data/Fig3Wollenhaupt.csv'
    OGdatadict, OGnames = csvtodict(OGdatapath,give_names=True)

    #Loop over the 3 different transfertime cases
    for tdays,sign in [(90,'-'),(180,':'),(360,'--')]:


        Rlist = []
        Mlist = []
        Slist = []
        Ilist = []
        #Writing Column Names
        csvwrite.writerow([f'Isp {tdays}',f'Inject Height {tdays} d',f'Sep. Mass {tdays} d',f'Trans. Eff. {tdays} d'])

        #Creating interpolated function from original injection height data
        OGIsps = OGdatadict[f'Inject Height {tdays} d Xdata']
        OGRinjs = OGdatadict[f'Inject Height {tdays} d Ydata']
        OGIsp_to_R_func = interp1d(OGIsps,OGRinjs)

        for Isp in range(260,3600,20):
            #Calculating Rinj for Isp from original curve
            Given_Rinj = OGIsp_to_R_func(Isp)
            #Running Model
            Mi, Si = OHBModel(I_sp=Isp, P_sat=2500.,t_trans=tdays*24*3600.,M_dry=1000.,R_f=23222.*10**3,launcher='Soyuz',R_inj_v=Given_Rinj)
            Rlist.append(Given_Rinj)
            Mlist.append(Mi)
            Slist.append(Si)
            Ilist.append(Isp)
            csvwrite.writerow([Isp,Given_Rinj,Mi,Si])

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



    #Second Figure Set- up
    csvwrite2 = writer(open('Data/launcherdataRinput.csv','w+'))
    fig2, axx = plt.subplots()
    axx2 = axx.twinx()
    fig2dict = {}
    axx.set_xlabel('Specific Impulse [s]')
    axx.set_ylabel('Injection Height [km],Separation Mass[kg]')
    axx2.set_ylabel('Transfer Efficiency [%]')

    #Loading Original Data to use the injection height input.
    OGdatapath2 = 'Data/Fig4Wollenhaupt.csv'
    OGdatadict2, OGnames2 = csvtodict(OGdatapath2,give_names=True)

    for launcher, sign2 in [('Ariane62','--'),('Ariane64',':'),('Soyuz','-')]:
        datalist = [[],[],[]]
        Ilist2 = []
        csvwrite2.writerow([f'Isp {launcher}',f'Inject Height {launcher}',f'Sep. Mass {launcher}',f'Trans. Eff. {launcher}'])

        OGIsps2 = OGdatadict2[f'Inject Height Xdata']
        OGRinjs2 = OGdatadict2[f'Inject Height Ydata']
        OGIsp_to_R_func2 = interp1d(OGIsps2,OGRinjs2)
        for Isp in range(260,3600,20):
            Given_Rinj = OGIsp_to_R_func2(Isp)
            Mi, Si = OHBModel(I_sp=Isp, P_sat=2500.,t_trans=90*24*3600.,M_dry=1000.,R_f=23222.*10**3,launcher=launcher,R_inj_v=Given_Rinj)
            datalist[0].append(Given_Rinj)
            datalist[1].append(Mi)
            datalist[2].append(Si)
            Ilist2.append(Isp)
            csvwrite2.writerow([Isp,Given_Rinj,Mi,Si])
        fig2dict[f'Sline{launcher}'], = axx2.plot(Ilist2,datalist[2], linestyle=sign2,color='darkorange',label=f'Transfer Efficiency {launcher}')
        fig2dict[f'Mline{launcher}'], = axx.plot(Ilist2,datalist[1], linestyle=sign2,color='k',label=f'Separation Mass {launcher}')
    Rline, = axx.plot(Ilist2,datalist[0],'g',label='Injection Height')

    handles2 = [Rline,fig2dict['SlineAriane62'],fig2dict['SlineAriane64'],fig2dict['SlineSoyuz'],fig2dict['MlineAriane62'],fig2dict['MlineAriane64'],fig2dict['MlineSoyuz']]

    fig2.legend(handles=handles2,loc='upper right',bbox_to_anchor=(0.88,0.88),ncol=2)
    fig2.suptitle('Comparison of Different Launchers - Model')
    plt.show()
