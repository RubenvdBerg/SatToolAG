from openmdao.api import ExplicitComponent
from math import sqrt
from numpy import exp

class MBOne(ExplicitComponent):
    
    def setup(self):
        self.add_input('M_batt')
        self.add_input('M_sa')

        self.add_output('t_tot')

    def compute(self, inputs, outputs):
        G_sc    = 1361      #Solar constant in [W/m2]
        eta_sa  = 0.375     #Solar Array efficiency in [-]
        Z_sa    = 2.8       #Solar Array Specific Area in [kg/m2]
        E_sp    = (65*3600) #Specific Energy of battery in [J/kg]

        A_sa    = inputs['M_sa']/Z_sa   #Solar Array area in [m2]
        P_sa    = A_sa*G_sc*eta_sa      #Solar Array Power in [W]
        C_batt  = inputs['M_batt']*E_sp #Battery Capacity in [J]

        M_0 = 150           #Initial Wet Mass of Satellite in [kg]
        R_0 = 6778000       #Initial Orbit Radius in [m]
        R_f = 7578000       #Final Orbit Radius in [m]
        mu  = 398600*10**9  #Earth's gravitational constant in []
        v_e = 9810          #Exhaust Velocity of Thruster in [m/s]

        DV_tot  = sqrt(mu/R_0)*(sqrt(2*R_f/(R_f+R_0))-1)+sqrt(mu/R_f)*(1-sqrt(2*R_0/(R_f+R_0))) #Total DeltaV required in [m/s]
        M_p     = M_0*(1-exp(-DV_tot/v_e))                                                      #Propellant Mass required in [kg]

        M_u     = 1     #Payload Mass in [kg]
        M_ps    = 50    #Propulsion System Mass in [kg]
        P_req   = 100   #Required Household Power in [W]
        eta_dis = 0.85  #Discharge efficiency in [-]
        P_th    = 250   #Thrust Phase Power required in [W]
        T_0     = 0.015 #Thrust of propulsion system in [N]

        #Check for Continuous Thrusting
        if P_th-P_sa < 0:
            print ('Continuous Thrusting Available')

        M_d     = M_0-(M_u+M_ps+M_p)    #Left over Mass in [kg]
        t_c     = C_batt/(P_sa-P_req)   #Cycle Charging time in [s]
        t_dc    = C_batt*eta_dis/(P_th) #Cycle Discharging time in [s]

        #Iteration Setup
        Mi      = 150
        DV      = 0
        cycle   = 0

        #Cycle Iteration
        while DV<DV_tot:
            DVi     = (T_0/Mi)*t_dc     #Increase in DeltaV
            DV      += DVi              #Total DeltaV deliverd
            Mi      *= exp(-DVi/v_e)    #Current Total Mass
            cycle   += 1                #Cycle Number

        #linear overshoot correction
        cycle -= (DV-DV_tot)/DVi

        outputs['t_tot'] = (t_c+t_dc)*cycle

if __name__ == '__main__':
    from openmdao.api import Group, Problem
    p = Problem()
    p.model = Group()
    p.model.add_subsystem('test1',MBOne(),promotes=['*'])
    p.setup()
    p['M_sa'] = 10
    p['M_batt'] = 10
    p.run_model()
    print(p['t_tot'])
