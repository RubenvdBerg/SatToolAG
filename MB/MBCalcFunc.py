from math import sqrt
from numpy import exp

def MBatteryCalc(M_batt):
    '''Function that calculates and returns the total orbit raising time
    given a certain battery mass for a given/pre-defined demonstration satellite'''

    #Pre-Defined Satellite Values

    M_0     = 150            #Initial Wet Mass in [kg]
    R_0     = 6778000        #Initial Orbit Radius in [meters]
    R_f     = 7578000        #Final Orbit Radius in [meters]
    mu      = 398600*10**9   #gravitational constant for Earth in [m3/s2]
    v_e     = 9810           #exhaust velocity in [m/s]

    M_ps    = 50             #Propulsion System Mass in [kg]
    M_u     = 5              #Payload Mass in [kg]

    G_sc    = 1361           #Solar Constant in [W/m2]
    eta_sa  = 0.375          #Solar array efficiency [-]
    Z_sa    = 2.8            #Solar array specific area in [kg/m2]
    E_sp    = (65*3600)      #Battery specific energy in [J/kg]

    P_req   = 100            #Power required (house keeping) in [W]
    eta_dis = 0.85           #Discharge efficiency in [-]
    P_th    = 250            #Power required during thrusting in [W]
    T_0     = 0.015          #Thrust in [N]


    #Calculation of DeltaV required
    DV_tot  = sqrt(mu/R_0)*(sqrt(2*R_f/(R_f+R_0))-1)+sqrt(mu/R_f)*(1-sqrt(2*R_0/(R_f+R_0)))

    #Calculation of Propellant Mass
    M_p     = M_0*(1-exp(-DV_tot/v_e))

    #Calculation of Mass left over for battery and solar array
    M_d     = M_0-(M_u+M_ps+M_p)

    #Division of Battery and Solar Mass
    M_sa    = M_d - M_batt

    if M_sa < 0:
        print(f"M_batt is too high and must be chosen between 1 and {M_d}  kg")

    A_sa    = M_sa/Z_sa             #Solar Array Area
    P_sa    = A_sa*G_sc*eta_sa      #Solar Array Power
    C_batt  = M_batt*E_sp           #Battery Capacity

    M_d     = M_0-(M_u+M_ps+M_p)    #Left over Mass (to be divided between battery and sollar array)
    t_c     = C_batt/(P_sa-P_req)   #Charging time
    t_dc    = C_batt*eta_dis/P_th   #Discharging time

    #Iteration setup
    Mi      = 150
    DV      = 0
    cycle   = 0

    while DV<DV_tot:
            DVi     = (T_0/Mi)*t_dc
            DV      += DVi
            Mi      *= exp(-DVi/v_e)
            cycle   += 1

    #linear overshoot correction
    cycle -= (DV-DV_tot)/DVi #total amount of charging, discharging cycles

    t_tot = (t_c+t_dc)*cycle #total orbit manouvre time

    return t_tot


def MSolarCalc(M_sa):
    '''Function that calculates and returns the total orbit raising time
    given a certain solar array mass for a given/pre-defined demonstration satellite'''

    #Pre-Defined Satellite Values

    M_0     = 150            #Initial Wet Mass in [kg]
    R_0     = 6778000        #Initial Orbit Radius in [meters]
    R_f     = 7578000        #Final Orbit Radius in [meters]
    mu      = 398600*10**9   #gravitational constant for Earth in [m3/s2]
    v_e     = 9810           #exhaust velocity in [m/s]

    M_ps    = 50             #Propulsion System Mass in [kg]
    M_u     = 5              #Payload Mass in [kg]

    G_sc    = 1361           #Solar Constant in [m]
    eta_sa  = 0.375          #Solar array efficiency [-]
    Z_sa    = 2.8            #Solar array specific area in [kg/m2]
    E_sp    = (65*3600)      #Battery specific energy in [J/kg]

    P_req   = 100            #Power required (house keeping) in [W]
    eta_dis = 0.85           #Discharge efficiency in [-]
    P_th    = 250            #Power required during thrusting in [W]
    T_0     = 0.015          #Thrust in [N]


    #Calculation of DeltaV required
    DV_tot = sqrt(mu/R_0)*(sqrt(2*R_f/(R_f+R_0))-1)+sqrt(mu/R_f)*(1-sqrt(2*R_0/(R_f+R_0)))

    #Calculation of Propellant Mass
    M_p    = M_0*(1-exp(-DV_tot/v_e))

    #Calculation of Mass left over for battery and solar array
    M_d    = M_0-(M_u+M_ps+M_p)

    #Division of Battery and Solar Mass
    M_batt   = M_d - M_sa

    if M_batt < 0:
        print(f"M_sa is too high and must be chosen between 1 and {M_d}  kg")

    A_sa    = M_sa/Z_sa             #Solar Array Area
    P_sa    = A_sa*G_sc*eta_sa      #Solar Array Power
    C_batt  = M_batt*E_sp           #Battery Capacity

    M_d     = M_0-(M_u+M_ps+M_p)    #Left over Mass (to be divided between battery and sollar array)
    t_c     = C_batt/(P_sa-P_req)   #Charging time
    t_dc    = C_batt*eta_dis/P_th   #Discharging time

    #iteration setup
    Mi      = 150
    DV      = 0
    cycle   = 0

    while DV<DV_tot:
            DVi     = (T_0/Mi)*t_dc
            DV      += DVi
            Mi      *= exp(-DVi/v_e)
            cycle   += 1

    #linear overshoot correction
    cycle -= (DV-DV_tot)/DVi

    t_tot = (t_c+t_dc)*cycle

    return t_tot
