from openmdao.api import Group, ExplicitComponent, DirectSolver, pyOptSparseDriver, Problem
from dymos import declare_time, declare_state, declare_parameter
import numpy as np
import matplotlib.pyplot as plt
from openmdao.utils.assert_utils import assert_rel_error
import dymos as dm
_g = {'earth': 9.80665,
      'moon': 1.61544}


class LaunchVehicle2DEOM(ExplicitComponent):

    def initialize(self):
        self.options.declare('num_nodes', types=int)

        self.options.declare('central_body', values=['earth', 'moon'], default='earth',
                             desc='The central graviational body for the launch vehicle.')

        self.options.declare('CD', types=float, default=0.5,
                             desc='coefficient of drag')

        self.options.declare('S', types=float, default=7.069,
                             desc='aerodynamic reference area (m**2)')

    def setup(self):
        nn = self.options['num_nodes']

        # Inputs
        self.add_input('vx',
                       val=np.zeros(nn),
                       desc='x velocity',
                       units='m/s')

        self.add_input('vy',
                       val=np.zeros(nn),
                       desc='y velocity',
                       units='m/s')

        self.add_input('m',
                       val=np.zeros(nn),
                       desc='mass',
                       units='kg')

        self.add_input('theta',
                       val=np.zeros(nn),
                       desc='pitch angle',
                       units='rad')

        self.add_input('rho',
                       val=np.zeros(nn),
                       desc='density',
                       units='kg/m**3')

        self.add_input('thrust',
                       val=2100000 * np.ones(nn),
                       desc='thrust',
                       units='N')

        self.add_input('Isp',
                       val=265.2 * np.ones(nn),
                       desc='specific impulse',
                       units='s')

        # Outputs
        self.add_output('xdot',
                        val=np.zeros(nn),
                        desc='velocity component in x',
                        units='m/s')

        self.add_output('ydot',
                        val=np.zeros(nn),
                        desc='velocity component in y',
                        units='m/s')

        self.add_output('vxdot',
                        val=np.zeros(nn),
                        desc='x acceleration magnitude',
                        units='m/s**2')

        self.add_output('vydot',
                        val=np.zeros(nn),
                        desc='y acceleration magnitude',
                        units='m/s**2')

        self.add_output('mdot',
                        val=np.zeros(nn),
                        desc='mass rate of change',
                        units='kg/s')

        # Setup partials
        ar = np.arange(self.options['num_nodes'])

        self.declare_partials(of='xdot', wrt='vx', rows=ar, cols=ar, val=1.0)
        self.declare_partials(of='ydot', wrt='vy', rows=ar, cols=ar, val=1.0)

        self.declare_partials(of='vxdot', wrt='vx', rows=ar, cols=ar)
        self.declare_partials(of='vxdot', wrt='m', rows=ar, cols=ar)
        self.declare_partials(of='vxdot', wrt='theta', rows=ar, cols=ar)
        self.declare_partials(of='vxdot', wrt='rho', rows=ar, cols=ar)
        self.declare_partials(of='vxdot', wrt='thrust', rows=ar, cols=ar)

        self.declare_partials(of='vydot', wrt='m', rows=ar, cols=ar)
        self.declare_partials(of='vydot', wrt='theta', rows=ar, cols=ar)
        self.declare_partials(of='vydot', wrt='vy', rows=ar, cols=ar)
        self.declare_partials(of='vydot', wrt='rho', rows=ar, cols=ar)
        self.declare_partials(of='vydot', wrt='thrust', rows=ar, cols=ar)

        self.declare_partials(of='mdot', wrt='thrust', rows=ar, cols=ar)
        self.declare_partials(of='mdot', wrt='Isp', rows=ar, cols=ar)

    def compute(self, inputs, outputs):
        theta = inputs['theta']
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        vx = inputs['vx']
        vy = inputs['vy']
        m = inputs['m']
        rho = inputs['rho']
        F_T = inputs['thrust']
        Isp = inputs['Isp']

        g = _g[self.options['central_body']]
        CDA = self.options['CD'] * self.options['S']

        outputs['xdot'] = vx
        outputs['ydot'] = vy
        outputs['vxdot'] = (F_T * cos_theta - 0.5 * CDA * rho * vx**2) / m
        outputs['vydot'] = (F_T * sin_theta - 0.5 * CDA * rho * vy**2) / m - g
        outputs['mdot'] = -F_T / (g * Isp)

    def compute_partials(self, inputs, jacobian):
        theta = inputs['theta']
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        m = inputs['m']
        vx = inputs['vx']
        vy = inputs['vy']
        rho = inputs['rho']
        F_T = inputs['thrust']
        Isp = inputs['Isp']

        g = _g[self.options['central_body']]
        CDA = self.options['CD'] * self.options['S']

        jacobian['vxdot', 'vx'] = -CDA * rho * vx / m
        jacobian['vxdot', 'rho'] = -0.5 * CDA * vx**2 / m
        jacobian['vxdot', 'm'] = -(F_T * cos_theta - 0.5 * CDA * rho * vx**2) / m**2
        jacobian['vxdot', 'theta'] = -(F_T / m) * sin_theta
        jacobian['vxdot', 'thrust'] = cos_theta / m

        jacobian['vydot', 'vy'] = -CDA * rho * vy / m
        jacobian['vydot', 'rho'] = -0.5 * CDA * vy**2 / m
        jacobian['vydot', 'm'] = -(F_T * sin_theta - 0.5 * CDA * rho * vy**2) / m**2
        jacobian['vydot', 'theta'] = (F_T / m) * cos_theta
        jacobian['vydot', 'thrust'] = sin_theta / m

        jacobian['mdot', 'thrust'] = -1.0 / (g * Isp)
        jacobian['mdot', 'Isp'] = F_T / (g * Isp**2)


class LogAtmosphereComp(ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        self.options.declare('rho_ref', types=float, default=1.225,
                             desc='reference density, kg/m**3')
        self.options.declare('h_scale', types=float, default=8.44E3,
                             desc='reference altitude, m')

    def setup(self):
        nn = self.options['num_nodes']

        self.add_input('y', val=np.zeros(nn), desc='altitude', units='m')

        self.add_output('rho', val=np.zeros(nn), desc='density', units='kg/m**3')

        # Setup partials
        arange = np.arange(self.options['num_nodes'])
        self.declare_partials(of='rho', wrt='y', rows=arange, cols=arange, val=1.0)

    def compute(self, inputs, outputs):
        rho_ref = self.options['rho_ref']
        h_scale = self.options['h_scale']
        y = inputs['y']
        outputs['rho'] = rho_ref * np.exp(-y / h_scale)

    def compute_partials(self, inputs, jacobian):
        rho_ref = self.options['rho_ref']
        h_scale = self.options['h_scale']
        y = inputs['y']
        jacobian['rho', 'y'] = -(rho_ref / h_scale) * np.exp(-y / h_scale)



@declare_time(units='s')
@declare_state('x', rate_source='eom.xdot', units='m')
@declare_state('y', rate_source='eom.ydot', targets=['atmos.y'], units='m')
@declare_state('vx', rate_source='eom.vxdot', targets=['eom.vx'], units='m/s')
@declare_state('vy', rate_source='eom.vydot', targets=['eom.vy'], units='m/s')
@declare_state('m', rate_source='eom.mdot', targets=['eom.m'], units='kg')
@declare_parameter('thrust', targets=['eom.thrust'], units='N')
@declare_parameter('theta', targets=['eom.theta'], units='rad')
@declare_parameter('Isp', targets=['eom.Isp'], units='s')
class LaunchVehicleODE(Group):

    def initialize(self):
        self.options.declare('num_nodes', types=int,
                             desc='Number of nodes to be evaluated in the RHS')

        self.options.declare('central_body', values=['earth', 'moon'], default='earth',
                             desc='The central gravitational body for the launch vehicle.')

    def setup(self):
        nn = self.options['num_nodes']
        cb = self.options['central_body']

        if cb == 'earth':
            rho_ref = 1.225
            h_scale = 8.44E3
        elif cb == 'moon':
            rho_ref = 0.0
            h_scale = 1.0
        else:
            raise RuntimeError('Unrecognized value for central_body: {0}'.format(cb))

        self.add_subsystem('atmos',
                           LogAtmosphereComp(num_nodes=nn, rho_ref=rho_ref, h_scale=h_scale))

        self.add_subsystem('eom', LaunchVehicle2DEOM(num_nodes=nn, central_body=cb))

        self.connect('atmos.rho', 'eom.rho')


if __name__ == '__main__':


    #
    # Setup and solve the optimal control problem
    #
    p = Problem(model=Group())
    p.driver = pyOptSparseDriver()
    p.driver.options['dynamic_simul_derivs'] = True

    #
    # Initialize our Trajectory and Phase
    #
    traj = dm.Trajectory()

    phase = dm.Phase(ode_class=LaunchVehicleODE,
                     ode_init_kwargs={'central_body': 'earth'},
                     transcription=dm.GaussLobatto(num_segments=12, order=3, compressed=False))

    traj.add_phase('phase0', phase)
    p.model.add_subsystem('traj', traj)

    #
    # Set the options for the variables
    #
    phase.set_time_options(initial_bounds=(0, 0), duration_bounds=(10, 500))

    phase.set_state_options('x', fix_initial=True, ref=1.0E5, defect_ref=1.0)
    phase.set_state_options('y', fix_initial=True, ref=1.0E5, defect_ref=1.0)
    phase.set_state_options('vx', fix_initial=True, ref=1.0E3, defect_ref=1.0)
    phase.set_state_options('vy', fix_initial=True, ref=1.0E3, defect_ref=1.0)
    phase.set_state_options('m', fix_initial=True, ref=1.0E3, defect_ref=1.0)

    phase.add_control('theta', units='rad', lower=-1.57, upper=1.57)
    phase.add_design_parameter('thrust', units='N', opt=False, val=2100000.0)

    #
    # Set the options for our constraints and objective
    #
    phase.add_boundary_constraint('y', loc='final', equals=1.85E5, linear=True)
    phase.add_boundary_constraint('vx', loc='final', equals=7796.6961)
    phase.add_boundary_constraint('vy', loc='final', equals=0)

    phase.add_objective('time', loc='final', scaler=0.01)

    p.model.linear_solver = DirectSolver()

    #
    # Setup and set initial values
    #
    p.setup(check=True)

    p['traj.phase0.t_initial'] = 0.0
    p['traj.phase0.t_duration'] = 150.0
    p['traj.phase0.states:x'] = phase.interpolate(ys=[0, 1.15E5], nodes='state_input')
    p['traj.phase0.states:y'] = phase.interpolate(ys=[0, 1.85E5], nodes='state_input')
    p['traj.phase0.states:vx'] = phase.interpolate(ys=[0, 7796.6961], nodes='state_input')
    p['traj.phase0.states:vy'] = phase.interpolate(ys=[1.0E-6, 0], nodes='state_input')
    p['traj.phase0.states:m'] = phase.interpolate(ys=[117000, 1163], nodes='state_input')
    p['traj.phase0.controls:theta'] = phase.interpolate(ys=[1.5, -0.76], nodes='control_input')

    #
    # Solve the Problem
    #
    p.run_driver()

    #
    # Check the results.
    #
    print(p.get_val('traj.phase0.timeseries.time')[-1])
    print(p.get_val('traj.phase0.timeseries.states:y')[-1])
    print(p.get_val('traj.phase0.timeseries.states:vx')[-1])
    print(p.get_val('traj.phase0.timeseries.states:vy')[-1])
    #
    # Get the explitly simulated results
    #
    exp_out = traj.simulate()

    #
    # Plot the results
    #
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 8))

    axes[0].plot(p.get_val('traj.phase0.timeseries.states:x'),
                 p.get_val('traj.phase0.timeseries.states:y'),
                 marker='o',
                 ms=4,
                 linestyle='None',
                 label='solution')

    axes[0].plot(exp_out.get_val('traj.phase0.timeseries.states:x'),
                 exp_out.get_val('traj.phase0.timeseries.states:y'),
                 marker=None,
                 linestyle='-',
                 label='simulation')

    axes[0].set_xlabel('range (m)')
    axes[0].set_ylabel('altitude (m)')
    axes[0].set_aspect('equal')

    axes[1].plot(p.get_val('traj.phase0.timeseries.time'),
                 p.get_val('traj.phase0.timeseries.controls:theta'),
                 marker='o',
                 ms=4,
                 linestyle='None')

    axes[1].plot(exp_out.get_val('traj.phase0.timeseries.time'),
                 exp_out.get_val('traj.phase0.timeseries.controls:theta'),
                 linestyle='-',
                 marker=None)

    axes[1].set_xlabel('time (s)')
    axes[1].set_ylabel('theta (deg)')

    plt.suptitle('Single Stage to Orbit Solution Using Linear Tangent Guidance')
    fig.legend(loc='lower center', ncol=2)

    plt.show()
