from OHBModel import OHBModel
from csv import writer
import matplotlib.pyplot as plt
from csvtodict import csvtodict
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np


def create_fig3data(savepath,Isprange=(260,3600),step=20,inputR=False,inputM=False,graph=True):
    '''Recreate Wollenhaupt Figure 3 multi transfer time soyuz data for the current model for a certain Isp Range.
    With or without both Injection Height and Separation Mass as inputs.
    Saves the data in savepath '''
    #Open File to Write Data
    path = savepath
    csvwrite = writer(open(path,'w+'))
    #Set-Up plot 1

    if graph == True:
        fig, ax1 = plt.subplots()
        ax1.set_xlabel('Specific Impulse [s]')
        ax1.set_ylabel('Injection Height [km], Seperation Mass [kg]',)
        ax3 = ax1.twinx()
        ax3.set_ylabel('Transfer Efficiency [%]')
        ax3.set_ylim(top=600, bottom=0)
        fig.suptitle('Example MEO Transfer on an Soyuz - Model')
        linedict = {}

    #Loading Original Data to use the injection height input.
    OGdatapath = 'Data/Fig3Wollenhaupt.csv'
    OGdatadict, OGnames = csvtodict(OGdatapath,give_names=True)


    count = 0
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

        #Creating interpolated function from original sep mass data
        OGIspMs  = OGdatadict[f'Sep. Mass {tdays} d Xdata']
        OGMseps  = OGdatadict[f'Sep. Mass {tdays} d Ydata']
        OGIsp_to_M_func = interp1d(OGIspMs,OGMseps)

        (start, stop) = Isprange
        for Isp in np.arange(start,stop,step):
            #Calculating Rinj for Isp from original curve
            if inputR == True:
                Given_Rinj  = OGIsp_to_R_func(Isp)
            else:
                Given_Rinj  = None
            #Calculating Msep for Isp from original curve
            if inputM == True:
                Given_Msep  = OGIsp_to_M_func(Isp)
                launcher   = None
            else:
                Given_Msep  = None
                launcher    = 'Soyuz'

            #Running Model
            Ri, Mi, Si = OHBModel(
                i_sp=Isp,
                p_sat=2500.,
                t_trans=tdays * 24 * 3600.,
                m_dry=1000.,
                r_f=23222. * 10 ** 3,
                # eta_v = .41,
                launcher=launcher,
                r_inj_v=Given_Rinj,
                m_sep_v=Given_Msep)
            Rlist.append(Ri)
            Mlist.append(Mi)
            Slist.append(Si)
            Ilist.append(Isp)
            csvwrite.writerow([Isp,Ri,Mi,Si])
            # print(f'row being written, Ri:{Ri}')

        if graph == True:
            linedict[f"lineR{tdays}"], = ax1.plot(Ilist,Rlist,'g',linestyle=sign)
            linedict[f"lineM{tdays}"], = ax1.plot(Ilist,Mlist,'k',linestyle=sign)
            linedict[f"lineS{tdays}"], = ax3.plot(Ilist,Slist,'darkorange',linestyle=sign)

            linedict[f"lineR{tdays}"].set_label(f'Injection Height {tdays} days')
            linedict[f"lineM{tdays}"].set_label(f'Separation Mass {tdays} days')
            linedict[f"lineS{tdays}"].set_label(f'Transfer Efficiency {tdays} days')

    # # pdf = pd.read_csv(path,header=None)
    # # loc180 = pdf.loc[pdf[0]=='Isp 180'].index[0]
    # # loc360 = pdf.loc[pdf[0]=='Isp 360'].index[0]
    # # pdf90 = pdf.iloc[:loc180].reset_index(drop=True)
    # # pdf180 = pdf.iloc[loc180:loc360].reset_index(drop=True)
    # # pdf360 = pdf.iloc[loc360:].reset_index(drop=True)
    # # newpdf = pd.concat([pdf90,pdf180,pdf360],axis=1,ignore_index=True)
    # open(path, 'w').close()
    # newcsv = newpdf.to_csv(rf'{path}',index=False,index_label=False, header=None)
    if graph == True:
        #Set Correct Legend Order
        legendlist = []
        for i,days in [(0,90),(1,180),(2,360)]:
            for a in ['R','M','S']:
                legendlist.append(linedict[f"line{a}{days}"])
        #Create Legends with ordered handles and give location
        fig.legend(handles=legendlist,loc='lower left',bbox_to_anchor=(0.12,0.80),ncol=3)
        if graph == True:
            plt.show()


def create_fig4data(savepath,Isprange=(260,3600),step=20,inputR=False,inputM=False,graph=True):

    if graph == True:
        #Second Figure Set- up
        fig2, axx = plt.subplots()
        axx2 = axx.twinx()
        fig2dict = {}
        axx.set_xlabel('Specific Impulse [s]')
        axx.set_ylabel('Injection Height [km],Separation Mass[kg]')
        axx2.set_ylabel('Transfer Efficiency [%]')

    csvwrite2 = writer(open(savepath,'w+'))
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

        #Creating interpolated function from original sep mass data
        OGIspMs  = OGdatadict2[f'Sep. Mass {launcher} Xdata']
        OGMseps  = OGdatadict2[f'Sep. Mass {launcher} Ydata']
        OGIsp_to_M_func = interp1d(OGIspMs,OGMseps)

        (start,stop) = Isprange
        for Isp in np.arange(start,stop,step):# pdf = pd.read_csv(path,header=None)
    # loc180 = pdf.loc[pdf[0]=='Isp 180'].index[0]
    # loc360 = pdf.loc[pdf[0]=='Isp 360'].index[0]
    # pdf90 = pdf.iloc[:loc180].reset_index(drop=True)
    # pdf180 = pdf.iloc[loc180:loc360].reset_index(drop=True)
    # pdf360 = pdf.iloc[loc360:].reset_index(drop=True)
    # newpdf = pd.concat([pdf90,pdf180,pdf360],axis=1,ignore_index=True)
    # open(path, 'w').close()
    # newcsv = newpdf.to_csv(rf'{path}',index=False,index_label=False, header=None)
            #Calculating Rinj for Isp from original curve
            if inputR == True:
                Given_Rinj  = OGIsp_to_R_func2(Isp)
            else:
                Given_Rinj  = None
            #Calculating Msep for Isp from original curve
            if inputM == True:
                Given_Msep  = OGIsp_to_M_func(Isp)
                launch   = None
            else:
                Given_Msep  = None
                launch = launcher
            Ri, Mi, Si = OHBModel(i_sp=Isp, p_sat=2500., t_trans=90 * 24 * 3600., m_dry=1000., r_f=23222. * 10 ** 3, launcher=launch, r_inj_v=Given_Rinj, m_sep_v=Given_Msep)
            datalist[0].append(Ri)
            datalist[1].append(Mi)
            datalist[2].append(Si)
            Ilist2.append(Isp)
            csvwrite2.writerow([Isp,Ri,Mi,Si])
        if graph == True:
            fig2dict[f'Sline{launcher}'], = axx2.plot(Ilist2,datalist[2], linestyle=sign2,color='darkorange',label=f'Transfer Efficiency {launcher}')
            fig2dict[f'Mline{launcher}'], = axx.plot(Ilist2,datalist[1], linestyle=sign2,color='k',label=f'Separation Mass {launcher}')

    # pdf = pd.read_csv(path,header=None)
    # loc180 = pdf.loc[pdf[0]=='Isp Ariane64'].index[0]
    # loc360 = pdf.loc[pdf[0]=='Isp Soyuz'].index[0]
    # pdf90 = pdf.iloc[:loc180].reset_index(drop=True)
    # pdf180 = pdf.iloc[loc180:loc360].reset_index(drop=True)
    # pdf360 = pdf.iloc[loc360:].reset_index(drop=True)
    # newpdf = pd.concat([pdf90,pdf180,pdf360],axis=1,ignore_index=True)
    # open(path, 'w').close()
    # newcsv = newpdf.to_csv(rf'{path}',index=False,header=None,index_label=False)

    if graph == True:

        Rline, = axx.plot(Ilist2,datalist[0],'g',label='Injection Height')
        handles2 = [Rline,fig2dict['SlineAriane62'],fig2dict['SlineAriane64'],fig2dict['SlineSoyuz'],fig2dict['MlineAriane62'],fig2dict['MlineAriane64'],fig2dict['MlineSoyuz']]

        fig2.legend(handles=handles2,loc='upper right',bbox_to_anchor=(0.88,0.88),ncol=2)
        fig2.suptitle('Comparison of Different Launchers - Model')
        plt.show()

if __name__ == '__main__':
    create_fig3data('Data/fig3datatest.csv',inputR=False,inputM=False,graph=False)
