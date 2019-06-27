from openmdao.api import ExplicitComponent

class MB1Comp(ExplicitComponent):

    def setup(self):
        self.add_input('M_batt')
        self.add_input('M_sa')

        self.add_output('C_batt')
        self.add_output('P_sa')

    def compute(self, inputs, outputs):
        G_sc= 1361
        eta_sa= 0.375
        Z_sa= 2.8
        E_sp = (65*3600)

        A_sa    = inputs['M_sa']/Z_sa
        outputs['P_sa']    = A_sa*G_sc*eta_sa
        outputs['C_batt']  = inputs['M_batt']*E_sp

        self.declare_partials('*','*', method='fd')

#Verification Check
if __name__ == '__main__':
    from openmdao.api import Problem, Group
    prob = Problem()
    prob.model = Group()
    prob.model.add_subsystem('test1', MB1Comp(), promotes=['*'])

    prob.setup()
    prob['test1.M_batt'] = 1
    prob['test1.M_sa'] = 1
    prob.run_model()
    print(prob['C_batt'])
    print(prob['P_sa'])
