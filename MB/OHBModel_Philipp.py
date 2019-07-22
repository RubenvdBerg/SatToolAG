from scipy.optimize import newton, curve_fit
from math import exp,log,sqrt
from numpy import arange, linspace, array
from scipy.interpolate import interp1d
from csv import reader

#Ignore the functions besides OHBModel

def GetInitRadius(DV, Rf):
    '''Get Initial Orbit Radius [m] from DeltaV[m/s] and Final/Target Orbit Radius [m]'''
    mu = 3.98600*10**14
    def f(R0):
        return sqrt(mu/R0)*(sqrt(2*Rf/(Rf+R0))-1)+sqrt(mu/Rf)*(1-sqrt(2*R0/(Rf+R0)))-DV
    return newton(f,Rf)

def csvtocurve(func,path,param=None,graph=False,givepopt=False):
    '''Returns function that approximates the csv data in the given path for a given function transform,
    CSV file needs to be 2 columns with only data and no headers or (empty) strings

    func    = function form                                 (Example: lambda x,a,b: a*x+b)
    path    = pathstring                                    (Example: 'Data/datafile.csv')
    param   = list of first guesses for paramaters a,b,..   (Example: [1.0,0.1,0,8])
    grap    = if True returns graph of the datapoint and approximated curve
    givepopt= if True returns function as well as list of optimal parameters
    '''
    csvfile = open(path)
    dataset = reader(csvfile)
    Data = [[],[]]
    for i in dataset:
        Data[0].append(i[0])
        Data[1].append(i[1])
    DataX = array([float(i) for i in Data[0]])
    DataY = array([float(i) for i in Data[1]])
    if param != None:
        popt, pcov = curve_fit(func,DataX,DataY, p0=param)
    popt, pcov = curve_fit(func,DataX,DataY)

    if graph == True:
        xnew = linspace(DataX[0],DataX[-1],100)
        ynew = func(xnew,*popt)
        plt.plot(DataX,DataY,'o',xnew,ynew,'-')
        plt.show()
        yaverage = sum(DataY)/len(DataY)
        SStot = 0
        SSres = 0
        fnew = func(DataX,*popt)
        for y, f in zip(DataY,fnew):
            SStot += (y-yaverage)**2
            SSres += (y-f)**2

        R2 = 1-SSres/SStot
        print(f'R2 is {R2}')
    if  givepopt == True:
        return lambda x : func(x,*popt), popt
    if givepopt == False:
        return lambda x : func(x,*popt)

def csv_ip1d(path,graph=False,bounds=False,switch=False):
    '''Opens csv file and converts the data to an interpolated line fucntion.
    CSV file needs to be 2 columns with only data and no headers or (empty) strings

    path    = pathstring                                    (Example: 'Data/datafile.csv')
    param   = list of first guesses for paramaters a,b,..   (Example: [1.0,0.1,0,8])
    grap    = if True returns graph of the datapoint and approximated curve
    bounds  = if True returns boundaries of the interpolated function as well as the function
    switch  = if True plots x-values as y and vice versa
    '''

    csvfile = open(path)
    dataset = reader(csvfile)
    Data = [[],[]]
    for i in dataset:
        Data[0].append(i[0])
        Data[1].append(i[1])
    DataX = array([float(i) for i in Data[0]])
    DataY = array([float(i) for i in Data[1]])
    if switch == True:
        DataX, DataY = DataY, DataX
    function = interp1d(DataX,DataY)

    if graph == True:
        xnew = arange(DataX[0],DataX[-1],1)
        ynew = function(xnew)
        plt.plot(DataX,DataY,'o',xnew,ynew,'-')
        plt.show()

    if bounds ==  True:
        return function, [DataX[0],DataX[-1]]
    if bounds == False:
        return function


def OHBModel(I_sp, P_sat, t_trans, M_dry, R_f):
    '''Determines the Injection Height [km], Separation Mass [kg] and Transfer Efficiency [%] given the following parameters
    I_sp    = Specific Impulse in [s]
    P_sat   = Satellite Power in [W]
    t_trans = Allowed Transfer Time in [s]
    M_dry   = Dry Satellite Mass in [kg]
    R_f     = Target Orbit in [m]'''


    FPfunc  = csv_ip1d('Data/FP_Isp-Graph.csv')
    FPRatio = FPfunc(I_sp)*10**-6                   #Force-Power Ratio in [N/W]
    Thrust  = FPRatio*P_sat                         #Thrust in [N]
    mflow   = Thrust/(I_sp*9.81)                    #Mass Flow in [kg/s]
    Mp      = mflow*t_trans                         #Propellant Mass in [kg]
    DV      = I_sp*log(1+(Mp/M_dry))                #DeltaV in [m/s]
    R0      = GetInitRadius(DV,R_f)                 #Injection Radius in [m]
    Rinject = R0/1000-6371                          #Injection Height in [km]

    #Third order polynomial approximation of Ariane62 Launcher Data
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
    lineR, = ax1.plot(Ilist,Rlist,'g')
    lineM, = ax1.plot(Ilist,Mlist,'k')

    ax3 = ax1.twinx()
    lineS, = ax3.plot(Ilist,Slist,'r')
    ax3.set_ylabel('Transfer Efficiency [%]')
    fig.suptitle('Example MEO Transfer on an Ariane62 - Model')
    lineR.set_label('Injection Height')
    lineM.set_label('Separation Mass')
    lineS.set_label('Transfer Efficiency')
    fig.legend(loc='lower right',bbox_to_anchor=(0.85,0.2))
    # plt.show()
    # plt.plot(Ilist,DVlist)
    plt.show()
