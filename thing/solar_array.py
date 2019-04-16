from openmdao.api import ExplicitComponent, IndepVarComp, Group, Problem

class SolComp(ExplicitComponent):

    def setup(self):
        #input
        self.add_input("A_sa", units='m**2', desc='Solar Array Area')
        self.add_input("G_sc", units='W/m**2', desc='Solar Flux Constant')
        self.add_input("eta_sa", units=None, desc='Solar Array Conversion Efficiency')
        self.add_input("Z_sa", units='kg/m**2', desc='Solar Array Mass-Area Ratio')
        #outputs
        self.add_output("P_sa", units='W', desc='Solar Array Power')
        self.add_output("M_sa", units='kg', desc='Solar Array Mass')

        self.declare_partials('*','*','fd')

    def compute(self, inputs, outputs):
        outputs['M_sa'] = inputs['Z_sa']*inputs['A_sa']
        outputs['P_sa'] = inputs['A_sa']*inputs['G_sc']*inputs['eta_sa']

if __name__ == '__main__':
    ivc = IndepVarComp()
    ivc.add_output('A_sa', units='m**2', val=0.2305)
    ivc.add_output('G_sc', units='W/m**2', val=1361)
    ivc.add_output('eta_sa', units=None, val=0.375)
    ivc.add_output('Z_sa', units='kg/m**2', val=2.8)
    p = Problem()
    model = p.model = Group()
    model.add_subsystem('ivc',ivc,promotes=['*'])
    model.add_subsystem('SolArr',SolComp(),promotes=['*'])
    p.setup()
    p.run_model()

    print(p['P_sa'])
    print(p['M_sa'])
