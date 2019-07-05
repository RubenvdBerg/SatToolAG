from openmdao.api import ExplicitComponent, Problem, IndepVarComp, Group, view_model, ScipyOptimizeDriver, DirectSolver, SqliteRecorder, CaseReader, ExecComp
from NightCycle import MBOne

prob = Problem()
p = prob.model = Group()
indeps = p.add_subsystem('indeps', IndepVarComp(), promotes=['*'])
indeps.add_output('M_batt', 10)
indeps.add_output('M_sa', 10)
p.add_subsystem("OneComp", MBOne(),promotes=['*'])
p.add_subsystem('Constraint1', ExecComp( 'constraint1 = M_d - (M_batt + M_sa)'),promotes=['constraint1','M_d','M_sa','M_batt'])
prob.driver = ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'
# prob.driver.options['maxiter'] = 100
prob.driver.options['tol'] = 1e-10
# prob.driver.options['iprint'] = 2
# prob.driver.options['debug_print'] = ['desvars', 'ln_cons', 'nl_cons', 'objs','totals']
p.add_design_var('M_sa')
p.add_design_var('M_batt')
p.add_objective('t_tot', ref=4227031.1647298)
# p.add_constraint('M_batt', lower = 50)
p.add_constraint('M_sa', lower = 1)
p.add_constraint('constraint1', equals=0)

prob.setup()
prob.run_model()
p.add_constraint('M_batt', lower = float(prob['M_batt,min']))
print(prob['M_batt,min'])
prob.setup()
prob.set_solver_print(level=2)
p.approx_totals()
# view_model(prob)

prob.run_driver()
print('t_tot',prob['t_tot'],prob['t_tot']/(24*3600))
print('M_batt',prob['M_batt'])
print('M_sa',prob['M_sa'])
print('M_d',prob['M_d'])
