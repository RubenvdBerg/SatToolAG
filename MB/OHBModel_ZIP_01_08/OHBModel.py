from math import exp, log, sqrt

from interpolate import csv_ip1d
from curvefitter import csvtocurve


def OHBModel(i_sp, p_sat, t_trans, m_dry, r_f, eta_v=None, eta='Average', launcher=None, r_inj_v=None, m_sep_v=None, print_v=False,
             mode='curve', allvars=False):
    """Determines the Injection Height [km], Separation Mass [kg] and Transfer Efficiency [%] given the following parameters
    i_sp    = Specific Impulse in [s]
    p_sat   = Satellite Power in [W]
    t_trans = Allowed Transfer Time in [s]
    m_dry   = Dry Satellite Mass in [kg]
    r_f     = Target Orbit in [m]
    eta     = thrust Efficiency in [%] (Limited Options) or 'Average'
    launcher= Launchername from which data will be used to convert Injection Height to Separation Mass (Limited Options or add your own)
    r_inj_v = Optional Inject Orbit Height Value in [m], if not given calculated from maximum possible orbit transfer
    m_sep_v = Optional Separation Mass in [kg], if not given: calculated from launcher data
    print_v = Prints the outputs values to the console if set to True
    mode    = Choose between a curve or interpolation through the launcher data. Interpolation closer to original data, but introduces bounds
    allvars = If set to True returns a dictionary containing most calculated variables instead of the outputs. Mostly used for testing.

    outputs:
    r_inj = Injection Height in [km]
    M_sep = Separation Mass in [kg]
    T_eff = Transfer Efficiency in [%]
    """

    # Setting Errors and Parameter Options
    eta_options = ['30', '50', '70', '100', 'Average']
    if eta not in eta_options:
        raise ValueError(f"Invalid eta. Expected one of: {eta_options}")

    launcher_options = ['Ariane62', 'Soyuz', 'Ariane64', None]
    if launcher not in launcher_options:
        raise ValueError(f"Invalid launcher. Expected one of: {launcher_options}")

    if not 6371000 <= r_f <= 36000000:
        raise ValueError(f"Invalid Target Orbit. Must be between:6371000 and 36000000 [m]!!")

    modes = ['curve', 'interpolate']
    if mode not in modes:
        raise ValueError(f"Invalid mode. Expected one of: {modes}")

    # Creating Interpolating Function from Figure 2 in Wollenhaupt paper:
    # "Future Electric Propulsion Needs deduced from launcher and mission constraints"
    # Selects right data set based on 'eta'. 'eta' options only make sense if you see the figure.
    fp_func, bounds = csv_ip1d('Data/FP_Isp' + eta + '.csv', bounds=True)

    # Specific Impulse must be between the bounds of the input data above
    if not (bounds[0] <= i_sp <= bounds[1]):
        raise ValueError(f"For eta={eta}. I_sp must be between {bounds[0]:.1f} and {bounds[1]:.1f} seconds")

    # Calculating the main output parameters.
    g_0 = 9.81  # Earth's Gravity in [m/s2]
    fp_ratio = fp_func(i_sp) * 10**-6           # Force-Power Ratio in [N/W]
    if eta_v is not None:
        fp_ratio = 2*eta_v*p_sat/(i_sp*g_0)     # Force-Power Ratio in [N/W]
    thrust = fp_ratio * p_sat                   # Thrust in [N]
    m_flow = thrust / (i_sp * g_0)              # Mass Flow in [kg/s]
    m_p = m_flow * t_trans                      # Propellant Mass in [kg]
    dv = i_sp * g_0 * log(1 + (m_p / m_dry))    # DeltaV in [m/s] (Tsiolkovsky Equation)
    mu = 3.98600 * 10**14                       # Earth's Gravitational Parameter in [m3/s2]
    r_0 = mu / ((dv + sqrt(mu / r_f)) ** 2)     # Injection Radius in [m]
    r_e = 6371.                                 # Earth Radius in [km]

    # Calculate from maximum orbit transfer in allowed transfer time
    r_inj = r_0 / 1000. - r_e  # Injection Height in [km]

    # Setting minimal Orbit height
    if r_inj < 400:
        r_inj = 400
    # Set Inject Height if given
    if r_inj_v is not None:
        r_inj = r_inj_v

    # Recalculate Values in case of changed r_inj
    # print(f'Rinj {r_inj}, Isp {I_sp}')
    # print(f'r_0 was {r_0/1000}')
    r_0 = (r_inj + r_e) * 1000
    # print(f'r_0 is {r_0/1000}')
    # print(f'dv was {dv}')
    dv = sqrt(mu / r_0) - sqrt(mu / r_f)
    # print(f'dv is {dv}')
    # print(f'm_p was {m_p}')
    m_p = (exp(dv / (i_sp * g_0)) - 1) * m_dry
    # print(f'm_p is {m_p}')
    t_trans = m_p / m_flow
    # print(f'Transfer Time: {t_trans/(3600*24)}')
    # print()

    if launcher == 'Ariane62':
        launchpath = 'Data/Launchers/Ariane62MassRadiusWollenhaupt.csv'
        if mode == 'curve':
            # Third order polynomial approximation of Ariane62 Launcher Data (MEO)
            f = lambda x, a, b, c, d: a + b * x + c * x ** 2 + d * x ** 3
            f_rm = csvtocurve(f, launchpath)
        elif mode == 'interpolate':
            f_rm, r_bounds = csv_ip1d(launchpath, bounds=True)

    elif launcher == 'Soyuz':
        launchpath = 'Data/Launchers/Soyuz.csv'
        if mode == 'curve':
            # Fourth Order polynomial approximation of Soyuz Launcher Data (MEO)
            f = lambda x, a, b, c, d, e: a + b * x + c * x ** 2 + d * x ** 3 + e * x ** 4
            f_rm = csvtocurve(f, launchpath)
        elif mode == 'interpolate':
            f_rm, r_bounds = csv_ip1d(launchpath, bounds=True)
    elif launcher == 'Ariane64':
        launchpath = 'Data/Launchers/Ariane64.csv'
        if mode == 'curve':
            # Fourth Order polynomial approximation of Soyuz Launcher Data (MTO)
            f = lambda x, a, b, c, d, e: a + b * x + c * x ** 2 + d * x ** 3 + e * x ** 4
            f_rm = csvtocurve(f, launchpath)
        elif mode == 'interpolate':
            f_rm, r_bounds = csv_ip1d(launchpath, bounds=True)
    elif launcher == None and m_sep_v == None:
        raise RuntimeError('Neither launcher nor m_sep_v are specified. Cannot Calculate T_eff')

    # Errormessage for out of bounds interpolation
    if mode == 'interpolate':
        if not (r_bounds[0] <= r_inj <= r_bounds[1]):
            raise ValueError(
                f'To use the {launcher} interpolation curve, Injection Height must be between '
                f'{r_bounds[0]:.1f} km and {r_bounds[1]:.1f} km, but is {r_inj:.2f} km'
            )

    if m_sep_v != None:
        if launcher != None:
            raise RuntimeError(
                'You have specified both a separation mass value [m_sep_v] and a [launcher] to derive '
                'the Separation Mass [m_sep] from, pick one'
            )
        m_sep = m_sep_v
    else:
        m_sep = f_rm(r_inj)  # Separation Mass in [kg]

    t_eff = m_sep / (m_dry + m_p) * 100  # Transfer Efficiency in [%] (Amount of Satellites for given Separation Mass)

    if print_v == True:
        print(f"thrust-Power Ratio is {fp_ratio * 10 ** 6} mN/kW")
        print(f"Injection Height is {r_inj} km.")
        print(f"Separation Mass is {m_sep} kg.")
        print(f"Transfer Efficiency is {t_eff}%.")
    if allvars == True:
        dictionary = {'r_inj': r_inj, 'm_sep': m_sep, 't_eff': t_eff, 'fp_ratio': fp_ratio, 'g_0': g_0, 'thrust': thrust,
                      'm_flow': m_flow, 'm_p': m_p, 'dv': dv, 'mu': mu, 'r_0': r_0, 'r_e': r_e, 'r_f': r_f}
        return dictionary
    else:
        return r_inj, m_sep, t_eff


if __name__ == '__main__':
    from CreateErrorPlots import fig3errorplot, fig4errorplot
    from FiguresDataCreate import create_fig3data, create_fig4data

    '''The functions below creates the data and graphs from the model and compares with the original data
    If inputR is set to True, the original Injection Height Data is used directly instead of being calculated
    if inputM is set to True, the original Separation Mass Data is used directly instead of being calculated
    if erroronly is set to True only 1 graph per function is created showing only the errors,
     instead of 3 separate graphs showing both the data and errors of each separate transfer time (fig3) or launcher (fig4)'''

    # fig3errorplot('Data/Output/test3.csv',erroronly=True,inputR=True,inputM=False,savefile=False)
    # fig3errorplot('Data/Output/fig3data.csv', erroronly=True, inputR=False, inputM=False, savefile=True)
    fig3errorplot('Data/Output/test3.csv',erroronly=False,inputR=False,inputM=False,savefile=False)

    # fig4errorplot('Data/Output/test4.csv',erroronly=True,inputR=True,inputM=True,savefile=False)
    # create_fig3data('Data/Output/fig3error.csv',inputR=False,inputM=False,graph=True)
    # create_fig4data('Data/Output/fig4error.csv',inputR=False,inputM=False,graph=True)
