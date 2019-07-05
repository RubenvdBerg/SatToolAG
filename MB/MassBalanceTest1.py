from openmdao.api import ExplicitComponent, Problem, IndepVarComp, Group, view_model, ScipyOptimizeDriver, DirectSolver, SqliteRecorder, CaseReader, ExecComp
from MBGroup import MBGroup

prob = Problem()
prob.model = MBGroup()
prob.driver = ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'
# prob.driver.options['maxiter'] = 100
prob.driver.options['tol'] = 1e-10
# prob.driver.options['iprint'] = 2
prob.driver.options['debug_print'] = ['desvars', 'ln_cons', 'nl_cons', 'objs','totals']
prob.model.add_design_var('M_sa')
prob.model.add_design_var('M_batt')
prob.model.add_objective('t_tot')
prob.model.add_constraint('M_batt', lower = 1)
prob.model.add_constraint('M_sa', lower = 1)
prob.model.add_constraint('constraint1', equals=0)

prob.setup()
# prob.set_solver_print(level=2)
prob.model.approx_totals()
# view_model(prob)
# prob.run_model()

prob.run_driver()
print('t_tot',prob['t_tot'])
print('M_batt',prob['M_batt'])
print('M_sa',prob['M_sa'])
print('M_d',prob['M_d'])
