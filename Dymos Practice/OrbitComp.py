import numpy as np
from openmdao.api import ExplicitComponent
from dymos import declare_time, declare_state, declare_parameter
mu = 3.986592936294783e14
R_E = 6378137

period = 2.*np.pi * np.sqrt(R_E**3/mu)
#initial conditions
M0 = 150
r0 = 6378e3
theta0 = 0
vr0 = 0
vth0 = np.sqrt(mu/r0)
c_e0 = 9800
T0 = 0.015
M_dot0 = T0/c_e0

Mf = 100
rf = 7578e3
vrf = 0
vthf = np.sqrt(mu/rf)
# DV = np.sqrt(mu/r0)*(np.sqrt(2*rf/(rf+r0))-1)+np.sqrt(mu/rf)*(1-np.sqrt(2*r0/(rf+r0)))
@declare_time(units='s')
@declare_state('r', rate_source='r_dot', targets=['r'], units='m')
@declare_state('M', rate_source='M_dot', targets=['M'], units='kg')
@declare_state('theta', rate_source='theta_dot', targets=['theta'], units='rad')
@declare_state('vr', rate_source='vr_dot', targets=['vr'], units='m/s')
@declare_state('vth', rate_source='vth_dot', targets=['vth'], units='m/s')
# @declare_state('deltav', rate_source='deltav_dot', units='m/s')
@declare_parameter('u1', targets=['u1'], units=None)
@declare_parameter('c_e', targets=['c_e'], units='m/s')
@declare_parameter('T', targets=['T'], units='N')

class OrbitalComp(ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)

    def setup(self):
        nn = self.options['num_nodes']
        # Inputs
        self.add_input('M',
                       val=np.ones(nn)*M0,
                       desc='mass of the satellite',
                       units='kg')
        self.add_input('r',
                       val=np.ones(nn)*r0,
                       desc='radius from center of attraction',
                       units='m')
        self.add_input('theta',
                       val=np.zeros(nn),
                       desc='anomaly term',
                       units='rad')
        self.add_input('vr',
                       val=np.zeros(nn),
                       desc='local vertical velocity component',
                       units='m/s')
        self.add_input('vth',
                       val=np.ones(nn)*vth0,
                       desc='local horizontal velocity component',
                       units='m/s')
        self.add_input('u1',
                       val=np.zeros(nn),
                       desc='thrust angle above local horizontal',
                       units=None)
        self.add_input('c_e',
                       val=np.ones(nn)*c_e0,
                       desc='effective exhaust velocity',
                       units='m/s')
        self.add_input('T',
                       val=np.ones(nn)*T0,
                       desc='constant engine thrust',
                       units='N')
        # Outputs
        self.add_output('M_dot',
                        val=np.zeros(nn),
                        desc='rate of change of satellite mass',
                        units='kg/s')
        self.add_output('r_dot',
                        val=np.zeros(nn),
                        desc='rate of change of radius from center of attraction',
                        units='m/s')
        self.add_output('theta_dot',
                        val=np.zeros(nn),
                        desc='rate of change of anomaly term',
                        units='rad/s')
        self.add_output('vr_dot',
                        val=np.zeros(nn),
                        desc='rate of change of local vertical velocity component',
                        units='m/s**2')
        self.add_output('vth_dot',
                        val=np.zeros(nn),
                        desc='rate of change of local horizontal velocity component',
                        units='m/s**2')
        # self.add_output('deltav_dot',
        #                 val=np.zeros(nn),
        #                 desc='rate of change of delta-V',
        #                 units='m/s**2')
        self.add_output('pos_x',
                        val=np.zeros(nn),
                        desc='x-component of position',
                        units='m')
        self.add_output('pos_y',
                        val=np.zeros(nn),
                        desc='y-component of position',
                        units='m')

        # Setup partials
        ar = np.arange(self.options['num_nodes'])

        self.declare_partials(of='r_dot', wrt='vr', rows=ar, cols=ar, val=1.0)

        self.declare_partials(of='theta_dot', wrt='r', rows=ar, cols=ar)
        self.declare_partials(of='theta_dot', wrt='vth', rows=ar, cols=ar)

        self.declare_partials(of='vr_dot', wrt='r', rows=ar, cols=ar)
        self.declare_partials(of='vr_dot', wrt='vth', rows=ar, cols=ar)

        self.declare_partials(of='vth_dot', wrt='r', rows=ar, cols=ar)
        self.declare_partials(of='vth_dot', wrt='vr', rows=ar, cols=ar)
        self.declare_partials(of='vth_dot', wrt='vth', rows=ar, cols=ar)
        self.declare_partials(of='vth_dot', wrt='M', rows=ar, cols=ar)
        self.declare_partials(of='vth_dot', wrt='u1', rows=ar, cols=ar)
        self.declare_partials(of='vth_dot', wrt='T', rows=ar, cols=ar)

        # self.declare_partials(of='deltav_dot', wrt='M', rows=ar, cols=ar)
        # self.declare_partials(of='deltav_dot', wrt='u1', rows=ar, cols=ar)
        # self.declare_partials(of='deltav_dot', wrt='T', rows=ar, cols=ar)

        self.declare_partials(of='pos_x', wrt='r', rows=ar, cols=ar)
        self.declare_partials(of='pos_x', wrt='theta', rows=ar, cols=ar)

        self.declare_partials(of='pos_y', wrt='r', rows=ar, cols=ar)
        self.declare_partials(of='pos_y', wrt='theta', rows=ar, cols=ar)


    def compute(self, inputs, outputs):
        M = inputs['M']
        r = inputs['r']
        theta = inputs['theta']
        vr = inputs['vr']
        vth = inputs['vth']
        u1 = inputs['u1']
        c_e = inputs['c_e']
        T = inputs['T']

        outputs['M_dot'] = -T/c_e
        outputs['r_dot'] = vr
        outputs['theta_dot'] = vth / r
        outputs['vr_dot'] = vth**2 / r - mu / r**2
        outputs['vth_dot'] = u1*T/M - (vr * vth / r)
        # outputs['deltav_dot'] = u1*T/M

        outputs['pos_x'] = r * np.cos(theta)
        outputs['pos_y'] = r * np.sin(theta)

    def compute_partials(self, inputs, partials):
        M = inputs['M']
        r = inputs['r']
        theta = inputs['theta']
        vr = inputs['vr']
        vth = inputs['vth']
        u1 = inputs['u1']
        c_e = inputs['c_e']
        T = inputs['T']

        partials['theta_dot', 'r'] = -vth / r**2
        partials['theta_dot', 'vth'] = 1.0 / r

        partials['vr_dot', 'r'] = -vth**2 / r**2 + 2.0*mu / r**3
        partials['vr_dot', 'vth'] = 2 * vth / r

        partials['vth_dot', 'r'] = vr * vth / r**2
        partials['vth_dot', 'vr'] = -vth / r
        partials['vth_dot', 'vth'] = -vr / r
        partials['vth_dot', 'M'] = -u1*T/M**2
        partials['vth_dot', 'u1'] = T/M
        partials['vth_dot', 'T'] = u1/M

        # partials['deltav_dot', 'M'] = -u1*T/M**2
        # partials['deltav_dot', 'u1'] = T/M
        # partials['deltav_dot', 'T'] = u1/M

        partials['pos_x', 'r'] = np.cos(theta)
        partials['pos_x', 'theta'] = -r * np.sin(theta)

        partials['pos_y', 'r'] = np.sin(theta)
        partials['pos_y', 'theta'] = r * np.cos(theta)
