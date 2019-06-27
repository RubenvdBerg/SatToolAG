from openmdao.api import Group, IndepVarComp, ExecComp
from MB1 import MB1Comp
from MB2 import MB2Comp
from MB3 import MB3Comp

class MBGroup(Group):

    def setup(self):
        indeps = self.add_subsystem('indeps', IndepVarComp(), promotes=['*'])
        indeps.add_output('M_batt', 10)
        indeps.add_output('M_sa', 10)

        self.add_subsystem('BattSolar', MB1Comp(), promotes = ['*'])
        self.add_subsystem('MassTime', MB2Comp(), promotes=['*'])
        self.add_subsystem('OrbitCycle', MB3Comp(), promotes=['*'])
        self.add_subsystem('Constraint1', ExecComp( 'constraint1 = M_d - (M_batt + M_sa)'),promotes=['constraint1','M_d','M_sa','M_batt'])




if __name__ == '__main__':
    from openmdao.api import Problem
    prob = Problem()
    prob.model = MBGroup()

    prob.setup()
    prob.run_model()
    print('t_tot',prob['t_tot'])
