from openmdao.api import ExplicitComponent
from math import sqrt
from numpy import exp

class MB3Comp(ExplicitComponent):

    def setup(self):
        self.add_input('t_c')
        self.add_input('t_dc')

        self.add_output('t_tot')

    def compute(self, inputs, outputs):
        T_0     = 0.015
        Mi      = 150
        DV      = 0
        cycle   = 0

        R_0 = 6778000
        R_f = 7578000
        mu = 398600*10**9
        v_e = 9810

        DV_tot  = sqrt(mu/R_0)*(sqrt(2*R_f/(R_f+R_0))-1)+sqrt(mu/R_f)*(1-sqrt(2*R_0/(R_f+R_0)))

        while DV<DV_tot:
            # print (DV)
            DVi     = (T_0/Mi)*inputs['t_dc']
            DV      += DVi
            Mi      *= exp(-DVi/v_e)
            cycle   += 1

        #linear overshoot correction
        cycle -= (DV-DV_tot)/DVi
        outputs['t_tot'] = (inputs['t_c']+inputs['t_dc'])*cycle


if __name__ == '__main__':
    from openmdao.api import Problem, Group
    prob = Problem()
    prob.model = Group()
    prob.model.add_subsystem('test1', MB3Comp(), promotes=['*'])

    prob.setup()
    prob['test1.t_c'] = 135.8279347
    prob['test1.t_dc'] = 795.6
    prob.run_model()
    print('t_tot',prob['t_tot']/(3600*24))
