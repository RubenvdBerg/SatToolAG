from openmdao.api import Group
from dymos import declare_time, declare_state, declare_parameter
from OrbitComp import OrbitalComp

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

class OrbitODE(Group):

    def initialize(self):
        self.options.declare('num_nodes', types=int,desc='number of nodes')

    def setup(self):
        nn = self.options['num_nodes']

        self.add_subsystem('sat',OrbitalComp(num_nodes=nn))
