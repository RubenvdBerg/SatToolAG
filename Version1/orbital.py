from openmdao.api import ExplicitComponent, Problem, IndepVarComp

class VelocityComp(ExplicitComponent):

    def initialize(self):
        self.options.declare('d_t', default=1.)
    def setup(self):
        #input
        self.add_input('Ti', units='N', desc='Satellite Thrust at beginning of time-step' )
        self.add_input('Mi', units='kg', desc='Satellite Mass at beginning of time-step')
        self.add_input('vi', units='m/s', desc='Satellite Velocity at beginning of time-step')
        #independent variables
        self.add_input('mu', units='m**3/s**2', desc='Gravitational Parameter Central Body', val=(398600.4418*10**9))
        #output
        self.add_output('ve', units='m/s', desc='Satellite Velocity at end of time-step')
        self.add_output('re', units='m', desc='Satellite Circular Orbit Radius at end of time-step')

        self.declare_partials('*','*',method='fd')

    def compute(self, inputs, outputs):
        Ti = inputs['Ti']
        Mi = inputs['Mi']
        vi = inputs['vi']
        dt = self.options['d_t']

        outputs['ve'] = Ti/Mi*dt + vi
        outputs['re'] = inputs['mu']/(outputs['ve']**2)

import numpy as np
from math import sqrt
tstep = 0.1 #timestep size
N = 100 #number of iteration stepsb
R_0 = (400.+6378)*10**3 #[m]
mu = 398600.4418*10**9 #[m**3/s**2]
v_init = sqrt(mu/R_0)

ivc = IndepVarComp()
ivc.add_output('v0', val=v_init, units = 'm/s')
ivc.add_output('T0', val=0.015, units = 'N')
ivc.add_output('M0', val=150, units = 'kg')

p = Problem()
p.model.add_subsystem('init_con', ivc, promotes=['*'])
for i in range(N):
    p.model.add_subsystem(f"t_{i}", VelocityComp(d_t = tstep))
for i in range(N-1):
    p.model.connect(f"t_{i}.ve",f"t_{i+1}.vi")
p.model.connect('v0','t_0.vi')
p.model.connect('T0','t_0.Ti')
p.model.connect('M0','t_0.Mi')

v = [p['v0'],]
r = [R_0,]

for i in range(N):
    v.append(p[f"t_{i}.ve"])
    r.append(p[f"t_{i}.re"])
time = np.arange(N+1)*tstep

import matplotlib.pylab as plt
plt.plot(time,v)
plt.show

plt.plot(time,r)
plt.show
