from scipy.optimize import newton
from math import exp,log,sqrt
from interpolate import csv_ip1d
from curvefitter import csvtocurve

def GetInitRadius(DV, Rf):
    mu = 3.98600*10**14
    def f(R0):
        return sqrt(mu/R0)*(sqrt(2*Rf/(Rf+R0))-1)+sqrt(mu/Rf)*(1-sqrt(2*R0/(Rf+R0)))-DV
    return newton(f,Rf)



def OHBModel(I_sp, P_sat, t_trans, M_dry, R_f):
    FPfunc  = csv_ip1d('Data/FP_Isp-Graph.csv')
    FPRatio = FPfunc(I_sp)*10**-6                   #Force-Power Ratio in [N/W]
    Thrust  = FPRatio*P_sat                         #Thrust in [N]
    mflow   = Thrust/(I_sp*9.81)                    #Mass Flow in [kg/s]
    Mp      = mflow*t_trans                         #Propellant Mass in [kg]
    DV      = I_sp*log(1+(Mp/M_dry))                #DeltaV in [m/s]
    R0      = GetInitRadius(DV,R_f)                 #Injection Radius in [m]
    Rinject = R0/1000-6371                          #Injection Height in [km]

    #Linear approximation of Ariane62 Launcher Data
    f = lambda x,a,b,c,d : a+b*x+c*x**2+d*x**3
    RtoM = csvtocurve(f,'Data/Ariane62MassRadiusWollenhaupt.csv')
    Msep = RtoM(Rinject)

    SatR    = Msep/(M_dry+Mp)*100                   #Satellite Ratio in [%]
    # print(f"Thrust-Power Ratio is {FPRatio*10**6}")
    # print(f"Injection Height is {Rinject}.")
    # print(f"Separation Mass is {Msep}.")
    # print(f"Satellite Ratio is {SatR}.")
    return Rinject, Msep, SatR, DV


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    # OHBModel(I_sp=1500., P_sat=5000.,t_trans=120*24*3600.,M_dry=2000.,R_f=15000.*10**3)
    Rlist = []
    Mlist = []
    Slist = []
    Ilist = []
    DVlist = []

    for i in range(210,3600,100):
        Ri, Mi, Si, DV = OHBModel(I_sp=i, P_sat=5000.,t_trans=120*24*3600.,M_dry=2000.,R_f=23222.*10**3)
        Rlist.append(Ri)
        Mlist.append(Mi)
        Slist.append(Si)
        Ilist.append(i)
        DVlist.append(DV)

    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Specific Impulse [s]')
    ax1.set_ylabel('Injection Height [km], Seperation Mass [kg]',)
    ax1.plot(Ilist,Rlist,'g')
    ax1.plot(Ilist,Mlist,'k')

    ax3 = ax1.twinx()
    ax3.plot(Ilist,Slist,'r')
    ax3.set_ylabel('Transfer Efficiency [%]',color='r')
    # plt.show()
    # plt.plot(Ilist,DVlist)
    plt.show()
