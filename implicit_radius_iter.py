from openmdao.api import ImplicitComponent, IndepVarComp,Problem, NewtonSolver, DirectSolver, Group
import matplotlib.pylab as plt
from math import sqrt
import numpy as np
class RadiusComp(ImplicitComponent):
    """"Computes Radius change over a certain timestep"""

    def initialize(self):
        self.options.declare('d_t', default = 1., desc='timestep size')

    def setup(self):
        #input
        self.add_input('Ri',units='m',desc='Orbit Radius at beginning of timestep')
        self.add_input('Ti',units='N',desc='Satellite Thrust at beginning of timestep')
        self.add_input('Mi',units='kg',desc='Satellite Mass at beginning of timestep')
        #independent variables
        self.add_input('mu', units='m**3/s**2', desc='Gravitational Parameter Central Body', val=(398600.4418*10**9))
        #outputs
        self.add_output('Re',units='m',desc='Orbit Radius at end of timestep')

        self.declare_partials('*','*', method='fd')

    def apply_nonlinear(self, inputs, outputs, residuals):
        dt = self.options['d_t']
        Ri = inputs['Ri']
        mu = inputs['mu']
        Re = outputs['Re']
        residuals['Re'] = sqrt(mu/Ri)*(sqrt(2*Re/(Re+Ri))-1)+sqrt(mu/Re)*(1-sqrt(2*Ri/(Re+Ri)))-inputs['Ti']/inputs['Mi']*dt

    def guess_nonlinear(self, inputs, outputs, residuals):
        outputs['Re'] = inputs['Ri']

if __name__ == "__main__":
    #Instance of IndepVarComp
    ivc = IndepVarComp()
    ivc.add_output('R0', val=6778000, units='m')
    ivc.add_output('T0', val=0.015, units='N')
    ivc.add_output('M0', val=150., units='kg')
    ivc.add_output('mu', val=3.986004418*10**14, units='m**3/s**2')

    #Building Model
    p = Problem()
    model = p.model = Group()
    model.add_subsystem('init_cond', ivc, promotes=['*'])
    N = 2 #Number of iteration steps
    timestep = 3600 #in seconds
    for i in range(N):
        name = f"t_{i}"
        model.add_subsystem(name, RadiusComp(d_t = timestep))

    #Connecting variables
    for i in range(N-1):
        model.connect(f"t_{i}.Re",f"t_{i+1}.Ri")
    model.connect('R0','t_0.Ri')
    for i in range(N):
        model.connect('T0',f't_{i}.Ti')
        model.connect('M0',f't_{i}.Mi')
        model.connect('mu',f't_{i}.mu')

    #Setting Solvers
    model.nonlinear_solver = NewtonSolver(maxiter = 30, iprint = 2, rtol = 1e-10)
    model.linear_solver = DirectSolver()

    #Set-up and Run
    p.setup()
    p.run_model()

    #Plotting
    Re = [(p['init_cond.R0']-6378000)*10**-3,]
    for i in range(N):
        Re.append((p[f't_{i}.Re']-6378000)*10**-3)
    time = np.arange(N+1)*timestep
    plt.plot(time,Re)
    plt.show()
