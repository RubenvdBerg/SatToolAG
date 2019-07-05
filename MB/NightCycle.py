from openmdao.api import ExplicitComponent
from math import sqrt, asin, pi, cos, radians
from numpy import exp
from fasterimplicitradius import GetRadius
from GetMaxDark import GetDarkTime

class MBOne(ExplicitComponent):
    def initialize(self):
        self.options.declare('G_sc', default=1361., types=float)
        self.options.declare('eta_sa', default=0.375, types=float)
        self.options.declare('Z_sa', default=2.8, types=float)
        self.options.declare('E_sp', default=(65.*3600), types=float)
        self.options.declare('M_0', default=150., types=float)
        self.options.declare('R_0', default=6778000., types=float)
        self.options.declare('R_f', default=7478000., types=float)
        self.options.declare('mu', default=398600.*10**9, types=float)
        self.options.declare('v_e', default=2600*9.81, types=float)
        self.options.declare('M_u', default=70., types=float)
        self.options.declare('M_ps', default=15., types=float)
        self.options.declare('P_req', default=100., types=float)
        self.options.declare('eta_dis', default=0.85, types=float)
        self.options.declare('P_th', default=380., types=float)
        self.options.declare('T_0', default=0.0125, types=float)
        self.options.declare('theta', default=45., types=float)
        self.options.declare('eta_struct', default=0.3, types=float)

        self.options.declare('M_batt,min', default=1., types=float)

    def setup(self):
        self.add_input('M_batt', desc='Battery Mass in [kg]')
        self.add_input('M_sa', desc='Solar Array Mass in [kg]')

        self.add_output('t_tot', desc='Total Orbit Manouvre Time in [s]')
        self.add_output('M_d', desc='Left over mass in [kg]')
        self.add_output('M_batt,min', desc='Minimal Battery Mass')

    def compute(self, inputs, outputs):
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
        v_e = self.options['v_e']           #Exhaust Velocity of Thruster in [m/s]


        DV_tot  = sqrt(mu/R_0)*(sqrt(2*R_f/(R_f+R_0))-1)+sqrt(mu/R_f)*(1-sqrt(2*R_0/(R_f+R_0))) #Total DeltaV required in [m/s]
        M_p     = M_0*(1-exp(-DV_tot/v_e))  #Propellant Mass required in [kg]

        eta_struct  = self.options['eta_struct']    #Mass Fraction for structure etc in [-]
        M_s         = M_0*eta_struct                #Satellite Structural Mass in [kg]

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
            DVi     = (T_0/Mi)*t_dc         #Increase in DeltaV
            Ri      = GetRadius(DV=DVi,Ri = Ri,mu=mu)
            eta_dark  = asin(R_E/Ri)/pi     #Darkness percentage of total current orbit
            P_sadark = (1-eta_dark)*P_sa
            if P_sadark>P_req:
                t_c = C_batt/(P_sadark-P_req)
                # print("Charge time=",t_c)
            if P_sadark<P_req:
                print("Not enough power to charge battery")
            Mi      *= exp(-DVi/v_e)        #Current Total Mass
            t   += t_c+t_dc

        ShadeTime = max(GetDarkTime(R_0),GetDarkTime(R_f))
        outputs['M_batt,min'] = P_req*ShadeTime/(E_sp*eta_dis)
        #linear overshoot correction
        t -= (t_c+t_dc)*(Ri-R_f)/(Ri-Rimin1)
        #Outputs
        outputs['M_d']  = M_0-(M_u+M_ps+M_p+M_s)
        outputs['t_tot']= t

if __name__ == '__main__':
    from openmdao.api import Group, Problem
    import time
    start_time = time.time()

    p = Problem()
    p.model = Group()
    p.model.add_subsystem('test1',MBOne(),promotes=['*'])
    p.setup()
    p['M_sa'] = 5
    p['M_batt'] = 20
    p.run_model()
    print(p['M_d'])
    print("total orbit transfer time in days",p['t_tot']/(3600*24))
    print("Mbattmin is",p['M_batt,min'])
    print(f"executed in {(time.time()-start_time)} seconds")
