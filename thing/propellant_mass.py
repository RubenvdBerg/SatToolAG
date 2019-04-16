from openmdao.api import ExplicitComponent, Group, Problem, IndepVarComp
from numpy import exp
from math import sqrt

class MassPComp(ExplicitComponent):

    def setup(self):
        #input
        self.add_input("M_0", units="kg",desc='Total Initial Mass')
        self.add_input('R_0',units='m',desc='Initial Orbit Radius')
        self.add_input('R_f',units='m',desc='Final Orbit Radius')
        self.add_input('mu', units='m**3/s**2', desc='Gravitational Parameter Central Body')
        self.add_input("v_e", units="m/s",desc='Exhaust Velocity')

        #output
        self.add_output("DV_tot",units="m/s",desc='Total Delta V for the Orbit Maneauvre')
        self.add_output("M_p", units="kg",desc='Total Propellant Mass')

        self.declare_partials('*','*', method='fd')

    def compute(self, inputs, outputs):
        R_0 = inputs['R_0']
        mu = inputs['mu']
        R_f = inputs['R_f']
        DV_tot = outputs['DV_tot'] = sqrt(mu/R_0)*(sqrt(2*R_f/(R_f+R_0))-1)+sqrt(mu/R_f)*(1-sqrt(2*R_0/(R_f+R_0)))
        outputs['M_p'] = inputs['M_0']*(1-exp(-DV_tot/inputs['v_e']))

if __name__ == '__main__':
    ivc = IndepVarComp()
    ivc.add_output("R_0", units="m", val=6778000)
    ivc.add_output("R_f", units="m", val=7578000)
    ivc.add_output("mu", units="m**3/s**2", val=398600.4418*10**9)
    ivc.add_output("v_e", units="m/s", val=9810)
    ivc.add_output("M_0", units="kg", val=150)
    p = Problem()
    model = p.model = Group()
    model.add_subsystem("MassP", MassPComp(),promotes=["*"])
    model.add_subsystem("ic",ivc,promotes=["*"])


    p.setup()
    p.run_model()

    print(p['M_p'])
    print(p['DV_tot'])
