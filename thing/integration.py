from openmdao.api import ExplicitComponent, Problem, IndepVarComp, Group, view_model
from mass_velocity_iter import MassIterComp
from propellant_mass import MassPComp
from battery import BatteryComp
from solar_array import SolComp


ivc = IndepVarComp()

ivc.add_output('M_0', 150, units='kg',desc='Satellite Mass at first step')
ivc.add_output('R_0',6778000, units='m',desc='Initial Orbit Radius')
ivc.add_output('R_f',7578000, units='m',desc='Final Orbit Radius')
ivc.add_output('mu',(398600.4418*10**9), units='m**3/s**2', desc='Gravitational Parameter Central Body')
ivc.add_output('v_e', 9810, units='m/s', desc='Exhaust Velocity')

ivc.add_output("A_sa", 0.23, units='m**2', desc='Solar Array Area')
ivc.add_output("G_sc", 1361, units='W/m**2', desc='Solar Flux Constant')
ivc.add_output("eta_sa", 0.375, units=None, desc='Solar Array Conversion Efficiency')
ivc.add_output("Z_sa", 2.8, units='kg/m**2', desc='Solar Array Mass-Area Ratio')

ivc.add_output('M_u', 50, units='kg', desc='Payload Mass')
ivc.add_output('M_ps', 50, units='kg', desc='Propulsion System Mass')
ivc.add_output('E_sp', (65*3600), units='J/kg', desc='Battery Specific Energy')
ivc.add_output('P_req', 100,units='W', desc='Baseline Required Power')
ivc.add_output('eta_dis', 0.85, units=None, desc='Discharge Efficiency')
ivc.add_output('P_th', 250, units='W', desc='Required Power for Thrust')

ivc.add_output('step_0', 0, units=None, desc='Step number of first step')
ivc.add_output('DV_tot_0', 0, units='m/s', desc='Total Velocity of first step')
ivc.add_output('T_0', 0.015, units='N',desc='Constant Thrust Value')


#Building Model
p = Problem()
model = p.model = Group()
model.add_subsystem('init_cond', ivc, promotes=['*'])
N = 111 #Number of iteration steps

model.add_subsystem('propul', MassPComp())
model.add_subsystem('solar', SolComp())
model.add_subsystem('battery', BatteryComp())
massvel = model.add_subsystem('massvel', Group())

for i in range(N):
    name = f"istep_{i}"
    massvel.add_subsystem(name, MassIterComp(), promotes=['T_0','v_e','T_th'])
#Connecting variables
for i in range(N-1):
    massvel.connect(f"istep_{i}.M_e",f"istep_{i+1}.M_i")
    massvel.connect(f"istep_{i}.DV_tot_e",f"istep_{i+1}.DV_tot_i")
    massvel.connect(f"istep_{i}.step_e",f"istep_{i+1}.step_i")
model.connect('M_0','massvel.istep_0.M_i')
model.connect('step_0','massvel.istep_0.step_i')
model.connect('DV_tot_0','massvel.istep_0.DV_tot_i')

model.connect('M_0','propul.M_0')
model.connect('R_0','propul.R_0')
model.connect('R_f','propul.R_f')
model.connect('mu','propul.mu')
model.connect('v_e','propul.v_e')

model.connect('M_0','battery.M_0')
model.connect('M_u','battery.M_u')
model.connect('M_ps','battery.M_ps')
model.connect('E_sp','battery.E_sp')
model.connect('P_req','battery.P_req')
model.connect('eta_dis','battery.eta_dis')
model.connect('P_th','battery.P_th')
model.connect('solar.M_sa', 'battery.M_sa')
model.connect('solar.P_sa', 'battery.P_sa')
model.connect('propul.M_p', 'battery.M_p')

model.connect('A_sa','solar.A_sa')
model.connect('G_sc','solar.G_sc')
model.connect('eta_sa','solar.eta_sa')
model.connect('Z_sa','solar.Z_sa')

model.connect('T_0','massvel.T_0')
model.connect('v_e','massvel.v_e')
model.connect('battery.T_th','massvel.T_th')

#Setting Solvers
# model.nonlinear_solver = NewtonSolver(maxiter = 30, iprint = 2, rtol = 1e-10)
# model.linear_solver = DirectSolver()

#Set-up and Run
p.setup()
p.run_model()
print(p[f'massvel.istep_{N-1}.DV_tot_e'])
print(p['propul.DV_tot'])
view_model(p)

# #Plotting
# Re = [(p['init_cond.R0']-6378000)*10**-3,]
# for i in range(N):
#     Re.append((p[f'istep_{i}.Re']-6378000)*10**-3)
# time = np.arange(N+1)*timestep
# plt.plot(time,Re)
# plt.show()
