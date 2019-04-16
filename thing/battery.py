from openmdao.api import ExplicitComponent, Problem, IndepVarComp
from math import sqrt
import numpy as np

class BatteryComp(ExplicitComponent):

    def setup(self):
        #Parameter Inputs
        self.add_input('M_sa', units='kg', desc='Sollar Array Mass')
        self.add_input('M_0', units='kg', desc='Initial Mass')
        self.add_input('M_u', units='kg', desc='Payload Mass')
        self.add_input('M_ps', units='kg', desc='Propulsion System Mass')
        self.add_input('E_sp', units='J/kg', desc='Battery Specific Energy')
        self.add_input('P_req', units='W', desc='Baseline Required Power')
        self.add_input('eta_dis', units=None, desc='Discharge Efficiency')
        self.add_input('P_th', units='W', desc='Required Power for Thrust')
        #Variable Inputs
        self.add_input("M_p", units="kg",desc='Total Propellant Mass')
        self.add_input('P_sa', units='W', desc='Solar Array Power')
        #output
        self.add_output('M_batt', units='kg', desc='Battery Mass')
        self.add_output('T_ch', units='s', desc='Cycle Time of one charge phase')
        self.add_output('T_th', units='s', desc='Cycle Time of one thrust phase')

        self.declare_partials('*','*','fd')

    def compute(self, inputs, outputs):
        M_batt = outputs['M_batt'] = inputs['M_0'] - (inputs['M_p']+inputs['M_u']+inputs['M_sa']+inputs['M_ps'])
        C_batt = M_batt*inputs['E_sp']
        P_sa = inputs['P_sa']
        P_req = inputs['P_req']
        if P_sa - (inputs['P_th']+P_req) >= 0:
            outputs['T_th'] = 36000
            print('There is enough power to continiously thrust')
        outputs['T_ch'] = C_batt/(P_sa-P_req)
        outputs['T_th'] = C_batt*inputs['eta_dis']/(inputs['P_th']-(P_sa-P_req))



if __name__ == '__main__':
    p = Problem()
    ivc = IndepVarComp()
    ivc.add_output('M_0',150., units='kg')
    ivc.add_output('M_u',50., units='kg')
    ivc.add_output('M_ps',50., units='kg')
    ivc.add_output('M_sa',0.644, units='kg')
    ivc.add_output('M_p',6.2242, units='kg')
    ivc.add_output('E_sp', 65*3600, units='J/kg')
    ivc.add_output('P_req', 100  ,units='W')
    ivc.add_output('eta_dis', 0.85, units=None)
    ivc.add_output('P_th', 250, units='W')
    ivc.add_output('P_sa', 117.64,units='W')

    p.model.add_subsystem('init_cond',ivc,promotes=['*'])

    p.model.add_subsystem('mass',BatteryComp(),promotes=['*'])

    p.setup()
    p.run_model()
    print(p['M_batt'])
    print(p['T_ch']/3600)
    print(p['T_th']/3600)
