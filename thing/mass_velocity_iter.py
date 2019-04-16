from openmdao.api import ExplicitComponent, Problem, IndepVarComp, Group
from math import sqrt
import numpy as np

class MassIterComp(ExplicitComponent):
    """"Computes Mass over a certain step"""
    def setup(self):
        #input
        self.add_input('step_i', units=None, desc='Step number of previous step')
        self.add_input('T_0',units='N',desc='Constant Thrust Value')
        self.add_input('M_i',units='kg',desc='Satellite Mass at beginning of step')
        self.add_input('T_th', units='s', desc='Thrust Phase Duration')
        self.add_input('v_e', units='m/s', desc='Exhaust Velocity')
        self.add_input('DV_tot_i', units='m/s', desc='Total Velocity at the beginning of step')
        #outputs
        self.add_output('M_e',units='kg',desc='Satellite Mass at end of step')
        self.add_output('step_e', units=None, desc='Step number of this step')
        self.add_output('DV_tot_e', units='m/s', desc='Total Velocity at the end of step')

        self.declare_partials('*','*', method='fd')

    def compute(self, inputs, outputs):
        M_i = inputs['M_i']
        DVi = inputs['T_0']/M_i*inputs['T_th']
        outputs['DV_tot_e'] = inputs['DV_tot_i']+DVi
        outputs['M_e'] = np.exp(-DVi/inputs['v_e'])*inputs['M_i']
        outputs['step_e'] = inputs['step_i'] + 1

if __name__ == "__main__":
    #Instance of IndepVarComp
    ivc = IndepVarComp()
    ivc.add_output('step_0', 0, units=None, desc='Step number of previous step')
    ivc.add_output('T_0', 0.015, units='N',desc='Constant Thrust Value')
    ivc.add_output('M_0', 150, units='kg',desc='Satellite Mass at beginning of step')
    ivc.add_output('T_th', 10.255*3600, units='s', desc='Thrust Phase Duration')
    ivc.add_output('v_e', 9810, units='m/s', desc='Exhaust Velocity')
    ivc.add_output('DV_tot_0', 0, units='m/s', desc='Total Velocity at the beginning of step')

    #Building Model
    p = Problem()
    model = p.model = Group()
    model.add_subsystem('init_cond', ivc, promotes=['*'])
    N = 111 #Number of iteration steps

    for i in range(N):
        name = f"istep_{i}"
        model.add_subsystem(name, MassIterComp())

    #Connecting variables
    for i in range(N-1):
        model.connect(f"istep_{i}.M_e",f"istep_{i+1}.M_i")
        model.connect(f"istep_{i}.DV_tot_e",f"istep_{i+1}.DV_tot_i")
        model.connect(f"istep_{i}.step_e",f"istep_{i+1}.step_i")
    model.connect('M_0','istep_0.M_i')
    model.connect('step_0','istep_0.step_i')
    model.connect('DV_tot_0','istep_0.DV_tot_i')
    for i in range(N):
        model.connect('T_0',f'istep_{i}.T_0')
        model.connect('v_e',f'istep_{i}.v_e')
        model.connect('T_th',f'istep_{i}.T_th')

    #Setting Solvers
    # model.nonlinear_solver = NewtonSolver(maxiter = 30, iprint = 2, rtol = 1e-10)
    # model.linear_solver = DirectSolver()

    #Set-up and Run
    p.setup()
    p.run_model()
    print(p[f'istep_{N-1}.DV_tot_e'])

    # #Plotting
    # Re = [(p['init_cond.R0']-6378000)*10**-3,]
    # for i in range(N):
    #     Re.append((p[f'istep_{i}.Re']-6378000)*10**-3)
    # time = np.arange(N+1)*timestep
    # plt.plot(time,Re)
    # plt.show()
