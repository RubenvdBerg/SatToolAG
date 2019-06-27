from openmdao.api import ExplicitComponent
from math import sqrt
from numpy import exp

class MB2Comp(ExplicitComponent):

    def setup(self):
        self.add_input('P_sa')
        self.add_input('C_batt')

        self.add_output('M_d')
        self.add_output('t_c')
        self.add_output('t_dc')

    def compute(self, inputs, outputs):
        M_0 = 150
        R_0 = 6778000
        R_f = 7578000
        mu = 398600*10**9
        v_e = 9810

        DV_tot  = sqrt(mu/R_0)*(sqrt(2*R_f/(R_f+R_0))-1)+sqrt(mu/R_f)*(1-sqrt(2*R_0/(R_f+R_0)))
        M_p     = M_0*(1-exp(-DV_tot/v_e))

        M_u = 1
        M_ps = 50
        P_req = 100
        eta_dis = 0.85
        P_th = 250

        if P_th-inputs['P_sa'] < 0:
            print ('Continuous Thrusting Available')


        outputs['M_d'] = M_0-(M_u+M_ps+M_p)
        outputs['t_c'] = inputs['C_batt']/(inputs['P_sa']-P_req)
        outputs['t_dc'] = inputs['C_batt']*eta_dis/(P_th)#-(inputs['P_sa']-P_req))

        self.declare_partials('*','*', method='fd')


if __name__ == '__main__':
    from openmdao.api import Problem, Group
    prob = Problem()
    prob.model = Group()
    prob.model.add_subsystem('test1', MB2Comp(), promotes=['*'])

    prob.setup()
    prob['test1.P_sa'] = 1822.76785714
    prob['test1.C_batt'] = 234000
    prob.run_model()
    print('t_c',prob['t_c'])
    print('t_dc',prob['t_dc'])
    print('M_d',prob['M_d'])
