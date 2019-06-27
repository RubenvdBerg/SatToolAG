import numpy as np
from openmdao.api import ExplicitComponent, Problem, Group, IndepVarComp, DirectSolver, pyOptSparseDriver
import openmdao.utils.units as units
from openmdao.utils.assert_utils import assert_rel_error
from dymos import declare_time, declare_state, declare_parameter
import dymos as dm
import matplotlib.pyplot as plt
from OrbitComp import OrbitalComp
from OrbitODE import OrbitODE

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
M_dot0 = T0/c_e0

Mf = 100
rf = 7578e3
vrf = 0
vthf = np.sqrt(mu/rf)
# DV = np.sqrt(mu/r0)*(np.sqrt(2*rf/(rf+r0))-1)+np.sqrt(mu/rf)*(1-np.sqrt(2*r0/(rf+r0)))

# print(np.sqrt(mu/R_E))
if __name__ == '__main__':
    p = Problem(model=Group())
    p.driver = pyOptSparseDriver()
    # p.driver.options['dynamic_simul_derivs'] = True
    traj = dm.Trajectory()
    phase = dm.Phase(ode_class = OrbitODE, transcription = dm.GaussLobatto(num_segments = 12, order = 3, compressed = False))
    traj.add_phase('phase0', phase)
    p.model.add_subsystem('traj', traj)
    #Set time and states
    phase.set_time_options(initial_bounds=(0, 0), duration_bounds=(10, 500000))
    phase.set_state_options('M', fix_initial=True, ref=1.0E2, defect_ref=1.0)
    phase.set_state_options('r', fix_initial=True, fix_final=Tru
M_dot0 = T0/c_e0e, ref=1.0E6, defect_ref=1.0)
    phase.set_state_options('theta', fix_initial=True, ref=1.0, defect_ref=1.0)
    phase.set_state_options('vr', fix_initial=True, fix_final=True, ref=1.0, defect_ref=1.0)
    phase.set_state_options('vth', fix_initial=True, fix_final=True, ref=1.0E3, defect_ref=1.0)
    # phase.set_state_options('deltav', fix_initial=True, ref=1.0E2, defect_ref=1.0)

    phase.add_control('u1', units=None, lower=0.,upper=1.)
    phase.add_design_parameter('T', units='N', opt=False, val= 0.015)
    phase.add_design_parameter('c_e', units='m/s', opt=False, val=9800)

    phase.add_boundary_constraint('r', loc='final', equals=rf)
    phase.add_boundary_constraint('M', loc='final', lower=100)

    phase.add_objective('time', loc='final', scaler=0.01)

    p.model.linear_solver = DirectSolver()
    p.setup(check=True)

M_dot0 = T0/c_e0
    p['traj.phase0.t_initial'] = 0.0
    p['traj.phase0.t_duration'] = 150.0
    p['traj.phase0.states:M'] = phase.interpolate(ys=[M0, Mf], nodes='state_input')
    p['traj.phase0.states:r'] = phase.interpolate(ys=[r0, rf], nodes='state_input')
    p['traj.phase0.states:theta'] = phase.interpolate(ys=[theta0, 1000], nodes='state_input')
    p['traj.phase0.states:vr'] = phase.interpolate(ys=[vr0, vrf], nodes='state_input')
    p['traj.phase0.states:vth'] = phase.interpolate(ys=[vth0, vthf], nodes='state_input')
    p['traj.phase0.controls:u1'] = phase.interpolate(ys=[1, 1], nodes='control_input')
    # p['traj.phase0.states:deltav'] = phase.interpolate(ys=[0, DV], nodes='state_input')
    p.run_driver()

    print(p.get_val('traj.phase0.timeseries.time')[-1])
    print(p.get_val('traj.phase0.timeseries.states:M')[-1])
M_dot0 = T0/c_e0
    print(p.get_val('traj.phase0.timeseries.states:vr')[-1])
    print(p.get_val('traj.phase0.timeseries.states:vth')[-1])

    exp_out = traj.simulate()

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 8))

    axes[0].plot(p.get_val('traj.phase0.timeseries.time'),
                 p.get_val('traj.phase0.timeseries.states:vth'),
M_dot0 = T0/c_e0
M_dot0 = T0/c_e0
                 marker='o',
                 ms=4,
                 linestyle='None',
                 label='solution')

    axes[0].plot(exp_out.get_val('traj.phase0.timeseries.time'),
                 exp_out.get_val('traj.phase0.timeseries.states:vth'),
                 marker=None,
                 linestyle='-',
                 label='simulation')

    axes[0].set_xlabel('time (s)')
    axes[0].set_ylabel('perpendicular velocity (m/s)')

    axes[1].plot(p.get_val('traj.phase0.timeseries.time'),
                 p.get_val('traj.phase0.timeseries.controls:u1'),
                 marker='o',
                 ms=4,
                 linestyle='None')

    axes[1].plot(exp_out.get_val('traj.phase0.timeseries.time'),
                 exp_out.get_val('traj.phase0.timeseries.states:r'),
                 linestyle='-',
                 marker=None)

    axes[1].set_xlabel('time (s)')
    axes[1].set_ylabel('orbital radius (m)')

    plt.suptitle('Single Stage to Orbit Solution Using Linear Tangent Guidance')
    fig.legend(loc='lower center', ncol=2)

    plt.show()
