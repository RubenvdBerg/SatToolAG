from openmdao.api import ImplicitComponent
from math import sqrt
class RadiusComp(ImplicitComponent):
    """"Calculates the Radius for a given DeltaV increment"""
    def initialize(self):
        self.options.declare('mu', default=(398600.*10**9), types=float) #Gravitational Parameter Central Body (Default Earth) in [m3/s2]
    def setup(self):
        #input
        self.add_input('DeltaV', units='m/s', desc='Change in Velocity')
        self.add_input('R_i',units='m',desc='Orbit Radius after DV change')
        #outputs
        self.add_output('R_f',units='m',desc='Orbit Radius after DV change')

        self.declare_partials(of='*',wrt='*', method='fd')

    def apply_nonlinear(self, inputs, outputs, residuals):
        R_i = inputs['R_i']
        mu = self.options['mu']
        R_f = outputs['R_f']
        residuals['R_f'] = sqrt(mu/R_i)*(sqrt(2*R_f/(R_f+R_i))-1.)+sqrt(mu/R_f)*(1-sqrt(2*R_i/(R_f+R_i)))-inputs['DeltaV']
    def guess_nonlinear(self, inputs, outputs, residuals):
        R_i = float(inputs['R_i'])
        outputs['R_f'] = R_i

#Verification Test
if __name__ == '__main__':
    from openmdao.api import Problem, Group, NewtonSolver, ScipyKrylov
    p = Problem()
    model = p.model = Group()
    model.add_subsystem('radius',RadiusComp(), promotes=['*'])
    model.nonlinear_solver = NewtonSolver(maxiter = 30, iprint = 2, atol=1e-10, rtol=1e-12)
    model.linear_solver = ScipyKrylov()
    p.setup()
    p['R_i'] = 6778000
    p['DeltaV'] = 0.1
    p.run_model()

    print(p['radius.R_f']/1000)
