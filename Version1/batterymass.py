from openmdao.api import ExplicitComponent, Problem, IndepVarComp
from math import sqrt
import numpy as np

class MassComp(ExplicitComponent):

    def setup(self):
        #input
        self.add_input('M_sa', units='kg', desc='Sollar Array Mass')
        self.add_input('M_0', units='kg', desc='Initial Mass')
        self.add_input('M_u', units='kg', desc='Payload Mass')
        self.add_input('M_ps', units='kg', desc='Propulsion System Mass')

        #independent variables
        self.add_input('R0', units='km', desc='Initial Orbit Radius')
        self.add_input('Rf', units='km', desc='Final Orbit Radius')
        self.add_input('v_e', units='m/s', desc='Exhaust Velocity')

        #constants
        self.add_input('mu', units='m**3/s**2', desc='Gravitational Parameter Central Body', val=(398600.4418*10**9))

        #output
        self.add_output('M_batt', units='kg', desc='Battery Mass')
        self.add_output('M_p', units='kg', desc='Propellant Mass')
        self.add_output('DV', units='m/s', desc='Delta V')

        self.declare_partials('*','*')

    def compute(self, inputs, outputs):
        mu = inputs['mu']
        R0 = inputs['R0']
        Rf = inputs['Rf']
        M_0 = inputs['M_0']

        DV = sqrt(mu/R0)*(sqrt(2*Rf/(Rf+R0))-1) + sqrt(mu/Rf)*(1-sqrt((2*R0/(Rf+R0))))
        M_p = M_0/np.exp(DV/inputs['v_e'])

        outputs['M_batt'] = M_0 - (M_p+inputs['M_u']+inputs['M_sa']+inputs['M_ps'])

if __name__ == '__main__':
    p = Problem()
    ivc = IndepVarComp()
    ivc.add_output('M_0',150., units='kg')
    ivc.add_output('M_u',50., units='kg')
    ivc.add_output('M_ps',15., units='kg')
    ivc.add_output('M_sa',10., units='kg')
    ivc.add_output('R0',((400+6378)*10**3), units='m')
    ivc.add_output('Rf',((6378+1200)*10**3), units='m')
    ivc.add_output('v_e',(1000.*9.81), units='m/s')
    p.model.add_subsystem('init_cond',ivc,promotes=['*'])

    p.model.add_subsystem('mass',MassComp(),promotes=['*'])

    p.setup()
    p.run_model()
    print(p['M_batt'])
