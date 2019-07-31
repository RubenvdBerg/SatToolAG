from math import exp,log,sqrt
from interpolate import csv_ip1d
from curvefitter import csvtocurve
from csv import writer


def OHBModel(I_sp, P_sat, t_trans, M_dry, R_f, eta='30',launcher=None, R_inj_v=None,M_sep_v=None,print_v=False):
    '''Determines the Injection Height [km], Separation Mass [kg] and Transfer Efficiency [%] given the following parameters
    I_sp    = Specific Impulse in [s]
    P_sat   = Satellite Power in [W]
    t_trans = Allowed Transfer Time in [s]
    M_dry   = Dry Satellite Mass in [kg]
    R_f     = Target Orbit in [m]
    eta     = Thrust Efficiency in [%] (Limited Options) or 'Average'
    launcher= Launchername from which data will be used to convert Injection Height to Separation Mass (Limited Options or add your own)
    R_inj_v = Optional Inject Orbit Height Value in [m], if not given calculated from maximum possible orbit transfer
    M_inj_v = Optional Separation Mass in [kg], if not given: calculated from launcher data

    outputs:
    R_inj =
    M_sep =
    T_eff  =
    '''

    #Setting Errors and Parameter Options
    eta_options = ['30','50','70','100','Average']
    if eta not in eta_options:
        raise ValueError(f"Invalid eta. Expected one of: {eta_options}")

    launcher_options = ['Ariane62', 'Soyuz', 'Ariane64',None]
    if launcher not in launcher_options:
        raise ValueError(f"Invalid launcher. Expected one of: {launcher_options}")

    if not 6371000<=R_f<=36000000:
        raise ValueError(f"Invalid Target Orbit. Must be between:6371000 and 36000000 [m]!!" )

    #Creating Interpolating Function from Figure 2 in Wollenhaupt paper:
    #"Future Electric Propulsion Needs deduced from launcher and mission constraints"
    #Selects right data set based on 'eta'. 'eta' options only make sense if you see the figure.
    FPfunc, bounds  = csv_ip1d('Data/FP_Isp'+eta+'.csv', bounds=True)

    #Specific Impulse must be between the bounds of the input data above
    if not (bounds[0]<=I_sp<=bounds[1]):
        raise ValueError(f"For eta={eta}. I_sp must be between {bounds[0]:.1f} and {bounds[1]:.1f} seconds")

    FP_ratio= FPfunc(I_sp)*10**-6                   #Force-Power Ratio in [N/W]
    Thrust  = FP_ratio*P_sat                        #Thrust in [N]
    mflow   = Thrust/(I_sp*9.81)                    #Mass Flow in [kg/s]
    Mp      = mflow*t_trans                         #Propellant Mass in [kg]

    #Set Inject Height if given
    if R_inj_v != None:
        R_inj = R_inj_v
    #Otherwise calculate from maximum orbit transfer in allowed transfer time
    else:
        DV      = I_sp*9.81*log(1+(Mp/M_dry))           #DeltaV in [m/s] (Tsiolkovsky Equation)
        mu      = 3.98600*10**14                        #Earth's Gravitational Parameter in [m3/s2]
        #(For Low Thrust Circular Orbit Transfer DeltaV is equal to the difference in circular velocity)
        R0      = mu/((DV+sqrt(mu/R_f))**2)             #Injection Radius in [m]
        R_E     = 6371.                                 #Earth Radius in [km]
        R_inj   = R0/1000.-R_E                          #Injection Height in [km]
        #Setting minimal Orbit height
        if R_inj<400:
            R_inj = 400


    if launcher == 'Ariane62':
        #Third order polynomial approximation of Ariane62 Launcher Data (MEO)
        f = lambda x,a,b,c,d : a+b*x+c*x**2+d*x**3
        RtoM = csvtocurve(f,'Data/Launchers/Ariane62MassRadiusWollenhaupt.csv')
    elif launcher == 'Soyuz':
        #Fourth Order polynomial approximation of Soyuz Launcher Data (MEO)
        f = lambda x,a,b,c,d,e : a+b*x+c*x**2+d*x**3+e*x**4
        RtoM = csvtocurve(f,'Data/Launchers/Soyuz.csv')
    elif launcher == 'Ariane64':
        #Fourth Order polynomial approximation of Soyuz Launcher Data (MTO)
        f = lambda x,a,b,c,d,e : a+b*x+c*x**2+d*x**3+e*x**4
        RtoM = csvtocurve(f,'Data/Launchers/Ariane64.csv')
    elif launcher == None and M_sep_v == None:
        raise RuntimeError('Neither launcher nor M_sep_v are specified. Cannot Calculate T_eff')


    if M_sep_v != None:
        if launcher != None:
            raise RuntimeError('You have specified both a separation mass value [M_sep_v] and a [launcher] to derive the Separation Mass [Msep] from, pick one')
        Msep = M_sep_v
    else:
        Msep    = RtoM(R_inj)                             #Separation Mass in [kg]
    Teff    = Msep/(M_dry+Mp)*100                       #Transfer Efficiency in [%] (Amount of Satellites for given Separation Mass)

    if print_v == True:
        print(f"Thrust-Power Ratio is {FP_ratio*10**6} mN/kW")
        print(f"Injection Height is {R_inj} km.")
        print(f"Separation Mass is {Msep} kg.")
        print(f"Transfer Efficiency is {Teff}%.")
    # if R_inj_v == None:
    #     return R_inj, Msep, Teff


    return R_inj, Msep, Teff

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    # OHBModel(I_sp=1500., P_sat=5000.,t_trans=120*24*3600.,M_dry=2000.,R_f=15000.*10**3)
    Rlist = []
    Mlist = []
    Slist = []
    Ilist = []
    DVlist = []
    csvfile = writer(open('radiusdata2.csv','w+'))


    for i in range(200,3600,100):
        Ri, Mi, Si, DV = OHBModel(I_sp=i, P_sat=5000.,t_trans=120*24*3600.,M_dry=2000.,R_f=23222.*10**3)
        Rlist.append(Ri)
        Mlist.append(Mi)
        Slist.append(Si)
        Ilist.append(i)
        DVlist.append(DV)

    for Ri in Rlist:
        csvfile.writerow([Ri,2])


    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Specific Impulse [s]')
    ax1.set_ylabel('Injection Height [km], Seperation Mass [kg]',)
    lineR, = ax1.plot(Ilist,Rlist,'g')
    lineM, = ax1.plot(Ilist,Mlist,'k')

    ax3 = ax1.twinx()
    lineS, = ax3.plot(Ilist,Slist,'r')
    ax3.set_ylabel('Transfer Efficiency [%]')
    ax3.set_ylim(top=300, bottom=0)
    # ax4 = ax1.twinx()
    # fig.subplots_adjust(right=0.8)
    # def make_patch_spines_invisible(ax):
    #     ax.set_frame_on(True)
    #     ax.patch.set_visible(False)
    #     for sp in ax.spines.values():
    #         sp.set_visible(False)

    # lineV, = ax4.plot(Ilist,DVlist)
    # ax4.set_ylabel('DeltaV [m/s]',color='b')
    # ax4.spines['right'].set_position(('axes',1.15))
    # make_patch_spines_invisible(ax4)
    # ax4.spines['right'].set_visible(True)
    # lineV.set_label('DeltaV')
    fig.suptitle('Example MEO Transfer on an Ariane62 - Model')
    lineR.set_label('Injection Height')
    lineM.set_label('Separation Mass')
    lineS.set_label('Transfer Efficiency')

    fig.legend(loc='lower right',bbox_to_anchor=(0.8,0.2))
    # plt.show()



    plt.show()
