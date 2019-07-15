from openmdao.api import ExplicitComponent
from math import sqrt, asin, pi, cos, radians
from numpy import exp
from fasterimplicitradius import GetRadius
from GetMaxDark import GetDarkTime
import json


class MBOne(ExplicitComponent):
    def initialize(self):
        self.options.declare('M_0', default=150.)
        self.options.declare('I_sp', default=2600.)
        self.options.declare('M_u', default=70.)
        self.options.declare('M_ps', default=15.)
        self.options.declare('P_req', default=100.)
        self.options.declare('P_th', default=380.)
        self.options.declare('T_0', default=0.0125)

        self.options.declare('G_sc', default=1361.)
        self.options.declare('eta_sa', default=0.375)
        self.options.declare('Z_sa', default=2.8)
        self.options.declare('E_sp', default=(65.*3600))
        self.options.declare('R_0', default=6778000.)
        self.options.declare('R_f', default=7478000.)
        self.options.declare('mu', default=398600.*10**9)
        self.options.declare('eta_dis', default=0.85)
        self.options.declare('theta', default=45.)
        self.options.declare('M_st', default=45.)
        self.options.declare('Sat', default='arrowRIT', values=['arrowRIT','arrowHET','HAG1','EDRS-C','H2Sat1','Electra'])
        self.options.declare('SatClass')
        self.options.declare('M_batt,min', default=1.)

    def setup(self):
        self.add_input('M_batt', desc='Battery Mass in [kg]')
        self.add_input('M_sa', desc='Solar Array Mass in [kg]')

        self.add_output('t_tot', desc='Total Orbit Manouvre Time in [s]')
        self.add_output('M_d', desc='Left over mass in [kg]')
        self.add_output('M_batt,min', desc='Minimal Battery Mass')
        self.add_output('M_p', desc='Propellant Mass')

    def compute(self, inputs, outputs):

        Satdat = json.load(open("SatData.json"))

        for i in Satdat['Satellites']:
            if i['SatelliteName'] == self.options['Sat']:
                self.options['M_0']     = i['Wet Mass']
                self.options['T_0']     = i['Thrust']
                self.options['I_sp']    = i['Specific Impulse']
                self.options['P_th']    = i['Thrust Power']
                self.options['M_u']     = i['Payload Mass']
                self.options['M_ps']    = i['Propulsion System Mass']
                self.options['M_st']    = i['Structural Mass']
                self.options['P_req']   = i['Station Keeping Power']

                self.options['SatClass'] = i['Classification']

        #Checks for any unkowns
        if self.options['SatClass'] == "GEO":
            if self.options['M_u'] == "Unknown":
                self.options['M_u'] = 0.32*self.options['M_0']
            if self.options['M_st'] == "Unknown":
                self.options['M_st'] = 0.3*self.options['M_0']
            if self.options['M_ps'] == "Unknown":
                self.options['M_ps'] = 0.07*self.options['M_0']
            if self.options['P_req'] == "Unknown":
                self.options['P_req'] = 691.
            if self.options['P_th'] == "Unknown":
                print("Thrust Power needs to be known")

        g0      = 9.80665
        G_sc    = self.options['G_sc']      #Solar constant in [W/m2]
        eta_sa  = self.options['eta_sa']    #Solar Array efficiency in [-]
        Z_sa    = self.options['Z_sa']      #Solar Array Specific Area in [kg/m2]
        E_sp    = self.options['E_sp']      #Specific Energy of battery in [J/kg]
        theta   = self.options['theta']     #Worst Case Average Sun-Angle solar area in [degrees]

        A_sa    = inputs['M_sa']/Z_sa       #Solar Array area in [m2]
        C_batt  = inputs['M_batt']*E_sp     #Battery Capacity in [J]
        P_sa    = A_sa*G_sc*eta_sa*cos(radians(theta))  #Solar Array Power in [W]

        M_0 = self.options['M_0']           #Initial Wet Mass of Satellite in [kg]
        R_0 = self.options['R_0']           #Initial Orbit Radius in [m]
        R_f = self.options['R_f']           #Final Orbit Radius in [m]
        mu  = self.options['mu']            #Earth's gravitational constant in [m3/s2]
        I_sp = self.options['I_sp']           #Exhaust Velocity of Thruster in [m/s]


        DV_tot  = sqrt(mu/R_0)*(sqrt(2*R_f/(R_f+R_0))-1)+sqrt(muLauncher Choice/R_f)*(1-sqrt(2*R_0/(R_f+R_0))) #Total DeltaV required in [m/s]
        M_p     = M_0*(1-exp(-DV_tot/(I_sp*g0)))  #Propellant Mass required in [kg]


        M_st    = self.options['M_st']      #Satellite Structural Mass in [kg]
        M_u     = self.options['M_u']       #Payload Mass in [kg]
        M_ps    = self.options['M_ps']      #Propulsion System Mass in [kg]
        P_req   = self.options['P_req']     #Required Household Power in [W]
        eta_dis = self.options['eta_dis']   #Discharge efficiency in [-]
        P_th    = self.options['P_th']      #Thrust Phase Power required in [W]
        T_0     = self.options['T_0']       #Thrust of propulsion system in [N]



        #Check for Continuous Thrusting
        if P_th-P_sa < 0:
            print ('Continuous Thrusting Available')


        t_c     = C_batt/(P_sa-P_req)       #Cycle Charging time in [s]
        t_dc    = C_batt*eta_dis/(P_th)     #Cycle Discharging time in [s]

        #Iteration Setup
        Mi      = 150
        DV      = 0
        cycle   = 0
        Ri      = R_0
        R_E     = 6378000 #Earth Radius in [m]
        t       = 0

        #Cycle Iteration
        while Ri<R_f:
            DVi     = (T_0/Mi)*t_dc         #Increasein DeltaV
            Rimin1  = Ri
            Ri      = GetRadius(DV=DVi,Ri = Ri,mu=mu)
            eta_dark  = asin(R_E/Ri)/pi     #Darkness percentage of total current orbit
            P_sadark = (1-eta_dark)*P_sa
            if P_sadark>P_req:
                t_c = C_batt/(P_sadark-P_req)
                # print("Charge time=",t_c)
            if P_sadark<P_req:
                print("Not enough power to charge battery")
            Mi      *= exp(-DVi/(I_sp*g0))        #Current Total Mass
            t   += t_c+t_dc

        ShadeTime = max(GetDarkTime(R_0),GetDarkTime(R_f))
        outputs['M_batt,min'] = P_req*ShadeTime/(E_sp*eta_dis)
        #linear overshoot correction
        t -= (t_c+t_dc)*(Ri-R_f)/(Ri-Rimin1)
        #Outputs
        print(M_st)
        outputs['M_d']  = M_0-(M_u+M_ps+M_p+M_st)
        outputs['t_tot']= t
        outputs['M_p'] = M_p

if __name__ == '__main__':
    from openmdao.api import Group, Problem
    import time
    start_time = time.time()

    p = Problem()
    p.model = Group()
    p.model.add_subsystem('test1',MBOne(Sat='H2Sat1'),promotes=['*'])
    p.setup()
    p['M_sa'] = 100
    p['M_batt'] = 20
    p.run_model()
    print(p['M_d'])
    print("total orbit transfer time in days",p['t_tot']/(3600*24))
    print("Mbattmin is",p['M_batt,min'])
    print(f"executed in {(time.time()-start_time)} seconds")
