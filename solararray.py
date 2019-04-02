# from openmdao.api import ExplicitComponent
#
# class XComp(ExplicitComponent):
#
#     def setup(self):
#         self.add_input()
#         self.add_output()
#
#         self.declare_partials('*','*')
#
#     def compute(self, inputs, outputs):
#
#         output[''] =


from openmdao.api import ExplicitComponent

class SollarArrayComp(ExplicitComponent):

    def setup(self):
        self.add_input('eta_degr', desc='Degraded Efficiency')
        self.add_input('eta_sa', desc='Solar Array Efficiency')
        self.add_input('G_sc', units='W/m**2', val=1361, desc='Solar Constant')

        self.add_input('P_0', units='W',desc='Standby Power')



        self.add_output('M_sa', units='kg', desc='Sollar Array Mass')
        self.add_output('P_sa', units='W', desc='Sollar Array Power')
        self.declare_partials('*','*')

    def compute(self, inputs, outputs):

        output['P_sa'] = input['G_sc']*inputs['eta_degr']*inputs['eta_sa']*A_sa
