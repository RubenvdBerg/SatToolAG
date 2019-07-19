from curvefitter import csvtocurve
from interpolate import csv_ip1d
from scipy.interpolate import interp1d

def OHBModelR(I_sp, P_sat, t_trans, M_dry, R_inj):
    FPfunc  = csv_ip1d('Data/FP_Isp-Graph.csv')
    FPRatio = FPfunc(I_sp)*10**-6        #Force-Power Ratio in [N/W]
    Thrust  = FPRatio*P_sat                         #Thrust in [N]
    mflow   = Thrust/(I_sp*9.81)                    #Mass Flow in [kg/s]
    Mp      = mflow*t_trans                         #Propellant Mass in [kg]
    Rinject = R_inj

    #Linear approximation of Ariane62 Launcher Data
    f = lambda x,a,b,c,d : a+b*x+c*x**2+d*x**3
    RtoM = csvtocurve(f,'Data/Ariane62MassRadiusWollenhaupt.csv')
    Msep = RtoM(Rinject)

    SatR    = Msep/(M_dry+Mp)*100                   #Satellite Ratio in [%]
    return Msep, SatR

if __name__ == '__main__':
    from csv import reader
    import matplotlib.pyplot as plt
    csvdata = reader(open('Data/InjectHeight.csv'))
    plotlist = [[],[],[],[]]
    for data in csvdata:
        Isp     = float(data[0])
        Rinj    = float(data[1])
        Msep, SatR = OHBModelR(I_sp=Isp, P_sat=5000.,t_trans=120*24*3600.,M_dry=2000.,R_inj=Rinj)
        plotlist[0].append(Msep)
        plotlist[1].append(SatR)
        plotlist[2].append(Rinj)
        plotlist[3].append(Isp)

    SepMassData = reader(open('Data/SepMass.csv'))
    TransEff = reader(open('Data/TransEff.csv'))
    sepmasslist = [[],[]]
    transefflist = [[],[]]
    for i in SepMassData:
        sepmasslist[0].append(float(i[0]))
        sepmasslist[1].append(float(i[1]))

    for i in TransEff:
        transefflist[0].append(float(i[0]))
        transefflist[1].append(float(i[1]))

    TEfunc = interp1d(plotlist[3],plotlist[1])
    MSfunc = interp1d(plotlist[3],plotlist[0])

    MSerrorlist =[[],[]]
    TEerrorlist =[[],[]]
    for isp, ms in zip(sepmasslist[0],sepmasslist[1]):
        if isp > plotlist[3][0] and isp<plotlist[3][-1]:
            MSerrorlist[1].append(abs(ms - MSfunc(isp))/ms*100)
            MSerrorlist[0].append(isp)
    for isp, te in zip(transefflist[0],transefflist[1]):
        if isp > plotlist[3][0] and isp<plotlist[3][-1]:
            TEerrorlist[0].append(isp)
            TEerrorlist[1].append(abs(te - TEfunc(isp))/te*100)

    fig, ax1 = plt.subplots()
    fig.suptitle('Model Comparison for Injection Height input')
    fig.subplots_adjust(right=0.75)
    ax1.set_xlabel('Specific Impulse [s]')
    ax1.set_ylabel('Seperation Mass [kg]',)
    line1, = ax1.plot(plotlist[3],plotlist[2],'g')
    line2, = ax1.plot(plotlist[3],plotlist[0],'k')
    line3, = ax1.plot(sepmasslist[0],sepmasslist[1],'k',linestyle='--')

    def make_patch_spines_invisible(ax):
        ax.set_frame_on(True)
        ax.patch.set_visible(False)
        for sp in ax.spines.values():
            sp.set_visible(False)

    ax2 = ax1.twinx()
    line4, = ax2.plot(MSerrorlist[0],MSerrorlist[1],'k',linestyle=':')
    line5, = ax2.plot(TEerrorlist[0],TEerrorlist[1],'r',linestyle=':')
    ax2.set_ylabel('Errors [%]')
    ax2.spines['right'].set_position(('axes',1.08))
    make_patch_spines_invisible(ax2)
    ax2.spines['right'].set_visible(True)
    ax2.set_ylim(top=35)

    ax3 = ax1.twinx()
    line6, = ax3.plot(plotlist[3],plotlist[1],'r')
    line7, = ax3.plot(transefflist[0],transefflist[1],'r',linestyle='--')

    ax3.set_ylabel('Transfer Efficiency [%]')
    ax3.set_ylim(bottom=0)
    line1.set_label('Inject. Height Input [m]')
    line2.set_label('Model Sep. Mass [kg]')
    line3.set_label('Data Sep. Mass [kg]')
    line4.set_label('Sep. Mass Error [%]')
    line6.set_label('Model Trans. Eff. [%]')
    line7.set_label('Data Trans. Eff. [%]')
    line5.set_label('Trans. Eff. Error [%]')

    fig.legend(loc='upper center', bbox_to_anchor=(0.5, 0.06),
          ncol=7, fancybox=True, shadow=True)
    plt.show()
