from openmdao.api import ExplicitComponent
from math import sqrt

class PropulsionComp(ExplicitComponent):
    """
    A component that calculates the Mass Flow and Satellite Thrust from the Voltage and Current input
    """
    def setup(self):
        #Input
        self.add_input('Wm', units='Da', desc='Molecular Weight' )
        self.add_input('q', units='e', desc='Average Charge', val=1.0)
        self.add_input('I', units='A', desc='Input Current')
        self.add_input('V', units='V', desc='Input Voltage')
        #Output
        self.add_output('T', units='N', desc='Satellite Thrust' )
        self.add_output('mdot', units='kg/s', desc='Mass Flow' )

        self.declare_partials('*','*')

    def compute(self, inputs, outputs):
        Wm = inputs['Wm']
        q = inputs['q']
        I = inputs['I']
        V = inputs['V']
        outputs['T'] = sqrt((2*Wm*V)/q)*I
        outputs['mdot'] = (Wm*I)/q
