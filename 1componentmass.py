from openmdao.api import ExplicitComponent, Problem, IndepVarComp, Group, view_model, ScipyOptimizeDriver, DirectSolver, SqliteRecorder, CaseReader
from math import sqrt
import numpy as np

class FullComp(ExplicitComponent):

    def setup(self):
        #Inputs
        self.add_input('M_0', units='kg', desc='Initial Mass')
        self.add_input('R_0',units='m',desc='Initial Orbit Radius')
        self.add_input('R_f',units='m',desc='Final Orbit Radius')
        self.add_input('mu', units='m**3/s**2', desc='Gravitational Parameter Central Body')
        self.add_input('v_e', units='m/s',desc='Exhaust Velocity')
        self.add_input('A_sa', units='m**2', desc='Solar Array Area')
        self.add_input('G_sc', units='W/m**2', desc='Solar Flux Constant')
        self.add_input('eta_sa', units=None, desc='Solar Array Conversion Efficiency')
        self.add_input('Z_sa', units='kg/m**2', desc='Solar Array Mass-Area Ratio')
        self.add_input('M_u', units='kg', desc='Payload Mass')
        self.add_input('M_ps', units='kg', desc='Propulsion System Mass')
        self.add_input('E_sp', units='J/kg', desc='Battery Specific Energy')
        self.add_input('P_req', units='W', desc='Baseline Required Power')
        self.add_input('eta_dis', units=None, desc='Discharge Efficiency')
        self.add_input('P_th', units='W', desc='Required Power for Thrust')
        self.add_input('T_0',units='N',desc='Constant Thrust Value')

        #Outputs
        self.add_output('t_tot', units='s', desc='Total Time of the Orbit Manoeuvre')
        self.add_output('cycles', units=None, desc='Amount of charge and discharge cycles')


        self.declare_partials('*','*', method='fd')

    def compute(self, inputs, outputs):
        R_0     = inputs['R_0']
        mu      = inputs['mu']
        R_f     = inputs['R_f']
        P_req   = inputs['P_req']



        M_0     = inputs['M_0']
        v_e     = inputs['v_e']


        DV_tot  = sqrt(mu/R_0)*(sqrt(2*R_f/(R_f+R_0))-1)+sqrt(mu/R_f)*(1-sqrt(2*R_0/(R_f+R_0)))
        M_p     = M_0*(1-np.exp(-DV_tot/v_e))


        A_sa    = inputs['M_sa']/inputs['Z_sa']
        P_sa    = A_sa*inputs['G_sc']*inputs['eta_sa']


        C_batt  = M_batt*inputs['E_sp']



        if P_sa - (inputs['P_th']+P_req) >= 0:
            T_th = 36000
            print('There is enough power to continuously thrust')


        T_ch = C_batt/(P_sa-P_req)
        T_th = C_batt*inputs['eta_dis']/(inputs['P_th']-(P_sa-P_req))

        Mi      = M_0
        DV      = 0
        cycle   = 0

        while DV<DV_tot:
            DVi     = inputs['T_0']/Mi*T_th
            DV      += DVi
            Mi      *= np.exp(-DVi/v_e)
            cycle   += 1

        #linear overshoot correction
        cycle -= (DV-DV_tot)/DVi
        outputs['cycles'] = cycle
        outputs['t_tot'] = (T_ch+T_th)*cycle


if __name__ == '__main__':
    ivc = IndepVarComp()

    ivc.add_output('M_0', 150, units='kg',desc='Satellite Mass at first step')
    ivc.add_output('R_0',6778000, units='m',desc='Initial Orbit Radius')
    ivc.add_output('R_f',7578000, units='m',desc='Final Orbit Radius')
    ivc.add_output('mu',(398600*10**9), units='m**3/s**2', desc='Gravitational Parameter Central Body')
    ivc.add_output('v_e', 9810, units='m/s', desc='Exhaust Velocity')

    ivc.add_output("A_sa", 0.23, units='m**2', desc='Solar Array Area')
    ivc.add_output("G_sc", 1361, units='W/m**2', desc='Solar Flux Constant')
    ivc.add_output("eta_sa", 0.375, units=None, desc='Solar Array Conversion Efficiency')
    ivc.add_output("Z_sa", 2.8, units='kg/m**2', desc='Solar Array Mass-Area Ratio')

    ivc.add_output('M_u', 1, units='kg', desc='Payload Mass')
    ivc.add_output('M_ps', 50, units='kg', desc='Propulsion System Mass')
    ivc.add_output('E_sp', (65*3600), units='J/kg', desc='Battery Specific Energy')
    ivc.add_output('P_req', 100,units='W', desc='Baseline Required Power')
    ivc.add_output('eta_dis', 0.85, units=None, desc='Discharge Efficiency')
    ivc.add_output('P_th', 250, units='W', desc='Required Power for Thrust')

    ivc.add_output('T_0', 0.015, units='N',desc='Constant Thrust Value')

    #Building Model
    p = Problem()
    model = p.modelomponent is the basic building block of a model. You will always define components as a subclass of either ExplicitComponent or ImplicitComponent. Since our simple paraboloid function is explicit, we’ll use the ExplicitComponent. You see two methods defined:


    model.add_subsystem('init_cond', ivc, promotes=['*'])
    model.add_subsystem('comp', FullComp(), promotes=['*'])

    #Optimization Set-Up
    p.driver = ScipyOptimizeDriver()
    p.driver.options['optimizer'] = 'SLSQP'
    # p.driver.options['optimizer'] = 'COBYLA'
    p.driver.options
    model.linear_solver = DirectSolver(iprint=2)

    # model.add_design_var('eta_sa', lower = 0.01, upper=1)
    model.add_design_var('M_ps', lower=0.01, upper=100)
    model.add_constraint('con1',)
    model.add_objective('t_tot')

    #Case Recorder Setting
    recorder = SqliteRecorder('test.sql')
    p.driver.add_recorder(recorder)
    p.add_recorder(recorder)

    #Set-up and Run
    p.setup()
    p.set_solver_print(2)
    p.run_driver()
    # view_model(p)
    p.record_iteration('final')
    p.cleanup()

    cr = CaseReader('test.sql')
    drivercases = cr.list_cases('driver')
    case = cr.get_case(drivercases[0])
    print(sorted(case.outputs.keys()))

    print('P_req',['P_req'])
    print('A_sa',p['A_sa'])
    print('M_u',p['M_u'])
    print('M_ps',p['M_ps'])
    print(p['t_tot'])
    print(p['cycles'])
