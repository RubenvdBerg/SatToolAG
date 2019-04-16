from openmdao.api import ImplicitComponent, Problem, Group, NewtonSolver,ScipyKrylov, DirectSolver
from math import sqrt
class RadiusComp(ImplicitComponent):
    """"Calculates the Radius for a given DeltaV increment"""
    def setup(self):
        #input
        self.add_input('DeltaV', units='m/s', desc='Change in Velocity',val=1)
        self.add_input('Mi',units='kg',desc='Satellite Mass',val=150)
        self.add_input('R0',units='m',desc='Orbit Radius after DV change',val=6778000)
        #independent variables
        self.add_input('mu', units='m**3/s**2', desc='Gravitational Parameter Central Body', val=(398600.4418*10**9))
        #outputs
        self.add_output('Rf',units='m',desc='Orbit Radius after DV change')

        self.declare_partials(of='*',wrt='*', method='fd')

    def apply_nonlinear(self, inputs, outputs, residuals):
        R0 = inputs['R0']
        mu = inputs['mu']
        Rf = outputs['Rf']
        residuals['Rf'] = sqrt(mu/R0)*(sqrt(2*Rf/(Rf+R0))-1.)+sqrt(mu/Rf)*(1-sqrt(2*R0/(Rf+R0)))-inputs['DeltaV']
    def guess_nonlinear(self, inputs, outputs, residuals):
        outputs['Rf'] = 6378000



p = Problem()
model = p.model = Group()
model.add_subsystem('radius',RadiusComp())
model.nonlinear_solver = NewtonSolver(maxiter = 30, iprint = 2, atol=1e-10, rtol=1e-12)
model.linear_solver = ScipyKrylov()
p.setup()
p.run_model()

print(p['radius.Rf'])
