from math import exp,log,sqrt
from interpolate import csv_ip1d
from curvefitter import csvtocurve
from csv import writer


def OHBModel(I_sp, P_sat, t_trans, M_dry, R_f, eta='Average',launcher=None, R_inj_v=None,M_sep_v=None,print_v=False,mode='curve'):
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
    R_inj = Injection Height in [km]
    M_sep = Separation Mass in [kg]
    T_eff = Transfer Efficiency in [%]
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


    modes = ['curve','interpolate']
    if mode not in modes:
        raise ValueError(f"Invalid mode. Expected one of: {modes}")

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
    Mp      = mflow*t_trans                       #Propellant Mass in [kg]

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
        R_inj   += R_inj*.25
        #Setting minimal Orbit height
        if R_inj<400:
            R_inj = 400


    if launcher == 'Ariane62':
        launchpath = 'Data/Launchers/Ariane62MassRadiusWollenhaupt.csv'
        if mode == 'curve':
            #Third order polynomial approximation of Ariane62 Launcher Data (MEO)
            f = lambda x,a,b,c,d : a+b*x+c*x**2+d*x**3
            RtoM = csvtocurve(f,launchpath)
        elif mode == 'interpolate':
            RtoM, Rbounds = csv_ip1d(launchpath,bounds=True)
    elif launcher == 'Soyuz':
        launchpath =  'Data/Launchers/Soyuz.csv'
        if mode == 'curve':
            #Fourth Order polynomial approximation of Soyuz Launcher Data (MEO)
            f = lambda x,a,b,c,d,e : a+b*x+c*x**2+d*x**3+e*x**4
            RtoM = csvtocurve(f,launchpath)
        elif mode == 'interpolate':
            RtoM, Rbounds = csv_ip1d(launchpath,bounds=True)
    elif launcher == 'Ariane64':
        launchpath = 'Data/Launchers/Ariane64.csv'
        if mode == 'curve':
            #Fourth Order polynomial approximation of Soyuz Launcher Data (MTO)
            f = lambda x,a,b,c,d,e : a+b*x+c*x**2+d*x**3+e*x**4
            RtoM = csvtocurve(f,launchpath)
        elif mode == 'interpolate':
            RtoM, Rbounds = csv_ip1d(launchpath,bounds=True)
    elif launcher == None and M_sep_v == None:
        raise RuntimeError('Neither launcher nor M_sep_v are specified. Cannot Calculate T_eff')

    #Errormessage for out of bounds interpolation
    if mode == 'interpolate':
        if not (Rbounds[0]<=R_inj<=Rbounds[1]):
            raise ValueError(f'To use the {launcher} interpolation curve, Injection Height must be between {Rbounds[0]:.1f} km and {Rbounds[1]:.1f} km, but is {R_inj:.2f} km')

    if M_sep_v != None:
        if launcher != None:
            raise RuntimeError('You have specified both a separation mass value [M_sep_v] and a [launcher] to derive the Separation Mass [Msep] from, pick one')
        Msep = M_sep_v
    else:
        Msep    = RtoM(R_inj)           #Separation Mass in [kg]
    Teff    = Msep/(M_dry+Mp)*100       #Transfer Efficiency in [%] (Amount of Satellites for given Separation Mass)

    if print_v == True:
        print(f"Thrust-Power Ratio is {FP_ratio*10**6} mN/kW")
        print(f"Injection Height is {R_inj} km.")
        print(f"Separation Mass is {Msep} kg.")
        print(f"Transfer Efficiency is {Teff}%.")

    return R_inj, Msep, Teff

if __name__ == '__main__':
    from CreateErrorPlots import fig3errorplot, fig4errorplot
    from FiguresDataCreate import create_fig3data, create_fig4data

    '''The functions below creates the data and graphs from the model and compares with the original data
    If inputR is set to True, the original Injection Height Data is used directly instead of being calculated
    if inputM is set to True, the original Separation Mass Data is used directly instead of being calculated
    if erroronly is set to True only 1 graph per function is created showing only the errors,
     instead of 3 separate graphs showing both the data and errors of each separate transfer time (fig3) or launcher (fig4)'''

    fig3errorplot('Data/Output/test3.csv',erroronly=True,inputR=True,inputM=False,savefile=False)
    fig3errorplot('Data/Output/test3.csv',erroronly=True,inputR=False,inputM=False,savefile=False)
    fig3errorplot('Data/Output/test3.csv',erroronly=True,inputR=True,inputM=True,savefile=False)

    # fig4errorplot('Data/Output/test4.csv',erroronly=True,inputR=True,inputM=True,savefile=False)
    create_fig3data('Data/Output/fig3error.csv',inputR=False,inputM=False,graph=True)
    # create_fig4data('Data/Output/fig4error.csv',inputR=False,inputM=False,graph=True)
