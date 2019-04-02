from openmdao.api import ExplicitComponent

class TrajectoryComp(ExplicitComponent):
    """
    A component that calculates the acceleration, updates the Velocity and calculates the Circular Orbit Radius
    """
    def setup(self):
        #Input
        self.add_input('T', units='N', desc='Satellite Thrust' )
        self.add_input('M', units='kg', desc='Satellite Mass')
        self.add_input('mu', units='km**3/s**2', desc='Gravitational Parameter Central Body', val=398600.4418)
        #Output
        self.add_output('r', units='km', desc='Satellite Circular Orbit Radius')

        self.declare_partials('*','*')

    def compute(self, inputs, outputs):
        a = inputs['T']/inputs['M'] #Satellite acceleration
        #Discretization NEEDED!!
        v = v0 + a*dt #Satellite Velocity
        outputs['r'] = inputs['mu']/v**2
