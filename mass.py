from openmdao.api import ExplicitComponent
from math import sqrt

class MassComp(ExplicitComponent):

    def setup(self):
        #input
        self.add_input()
        self.add_input('M_sa', units='kg', desc='Sollar Array Mass')
        self.add_input('M_batt', units='kg', desc='Battery Mass')

        #independent variables
        self.add_input('R0', units='km', desc='Initial Orbit Radius')
        self.add_input('RF', units='km', desc='Final Orbit Radius')
        self.add_input('v_e', units='m/s', desc='Exhaust Velocity')

        #constants
        self.add_input('mu', units='km**3/s**2', desc='Gravitational Parameter Central Body', val=398600.4418)

        #output
        self.add_output('M_0', units='kg', desc='Initial Mass')

        self.declare_partials('*','*')

    def compute(self, inputs, outputs):
        DV = sqrt(inputs['mu']/inputs['RF'])-sqrt(inputs['mu']/inputs['R0'])
        MR = exp(DV/inputs['v_e'])
        output['M_0'] = M_p+inputs['M_batt']+inputs['M_sa']
