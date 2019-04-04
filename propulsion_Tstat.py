from openmdao.api import ExplicitComponent
from math import sqrt

class PropulsionComp(ExplicitComponent):
    """
    A component that calculates the Mass Flow and Satellite Thrust from Input Powers and Engine Specifications
    """
    def setup(self):
        #Input
        self.add_input('P_sa', units='W', desc='Solar Array Power' )
        sefl.add_input('P_batt', units='W', desc='Battery Output Power')

        #Independent Variables
        self.add_input('P_T', units='W', desc='Minimum Required Power for Thrust')
        self.add_input('P_0', units='W',desc='Required Standby Power')
        self.add_input('T_0', units='N', desc='Thrust Value')
        # self.add_input('v_e', units='m/s', desc='Exhaust Velocity')

        #Output
        self.add_output('T', units='N', desc='Satellite Thrust' )
        # self.add_output('mdot', units='kg/s', desc='Mass Flow' )

        self.declare_partials('*','*')

    def compute(self, inputs, outputs):
        P_sa = inputs['P_sa']
        P_0 = inputs['P_0']
        P_T = inputs['P_T']
        P_th = P_0 + P_T            #Threshold Power
        T_0 = inputs['T_0']

        if (P_sa + P_batt) >= P_th:
            outputs['T'] = T_0
        if (P_sa + P_batt) < P_th:
            outputs['T'] = 0

        # outputs['mdot'] = outputs['T']/inputs['v_e']
