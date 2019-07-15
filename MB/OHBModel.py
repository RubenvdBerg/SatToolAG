from scipy.optimize import newton
from math import exp, log,sqrt

def GetInitRadius(DV, Rf):
    mu = 3.98600*10**14
    def f(R0):
        return sqrt(mu/R0)*(sqrt(2*Rf/(Rf+R0))-1)+sqrt(mu/Rf)*(1-sqrt(2*R0/(Rf+R0)))-DV
    return newton(f,Rf)


def OHBModel(I_sp, P_sat, t_trans, M_dry, R_f):
    FPRatio = (34725.*I_sp**-0.8625)*10**-6         #Force-Power Ratio in [N/W]
    Thrust  = FPRatio*P_sat                         #Thrust in [N]
    mflow   = Thrust/(I_sp*9.81)                    #Mass Flow in [kg/s]
    Mp      = mflow*t_trans                         #Propellant Mass in [kg]
    DV      = I_sp*log(1+(Mp/M_dry))                #DeltaV in [m/s]
    R0      = GetInitRadius(DV,R_f)                 #Injection Radius in [m]
    Rinject = R0/1000-6371                          #Injection Height in [km]
    Msep    = 9849 - 0.728*(Rinject)                #Separation Mass in [kg]
    SatR    = Msep/(M_dry+Mp)*100                   #Satellite Ratio in [%]
    # print(f"Thrust-Power Ratio is {FPRatio*10**6}")
    # print(f"Injection Height is {Rinject}.")
    # print(f"Separation Mass is {Msep}.")
    # print(f"Satellite Ratio is {SatR}.")
    return Rinject, Msep, SatR

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    # OHBModel(I_sp=1500., P_sat=5000.,t_trans=120*24*3600.,M_dry=2000.,R_f=15000.*10**3)
    Rlist = []
    Mlist = []
    Slist = []
    Ilist = []

    for i in range(200,4000,100):
        Ri, Mi, Si = OHBModel(I_sp=i, P_sat=5000.,t_trans=120*24*3600.,M_dry=2000.,R_f=15000.*10**3)
        Rlist.append(Ri)
        Mlist.append(Mi)
        Slist.append(Si)
        Ilist.append(i)

    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Specific Impulse [s]')
    ax1.set_ylabel('Injection Height [km], Seperation Mass [kg]',)
    ax1.plot(Ilist,Rlist,'g')
    ax1.plot(Ilist,Mlist,'k')

    ax3 = ax1.twinx()
    ax3.plot(Ilist,Slist,'r')
    ax3.set_ylabel('Transfer Efficiency [%]',color='r')
    plt.show()

    fig, host = plt.subplots()
    fig.subplots_adjust(right=0.75)
