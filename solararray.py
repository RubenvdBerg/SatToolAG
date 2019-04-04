# from openmdao.api import ExplicitComponent
#
# class XComp(ExplicitComponent):
#
#     def setup(self):
#         #input
#         self.add_input()
#         #independent variables
#         self.add_input()
#         #output
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
        #input
        self.add_input('eta_degr', desc='Degraded Efficiency')

        #independent variables
        self.add_input('eta_sa', desc='Solar Array Efficiency')
        self.add_input('eta_EOL', desc='Degraded Efficiency at end of life')
        self.add_input('G_sc', units='W/m**2', val=1361, desc='Solar Constant')
        self.add_input('P_0', units='W',desc='Standby Power')
        self.add_input('MAr', desc='Mass-Area Ratio of Solar Cell Type')

        #output
        self.add_output('M_sa', units='kg', desc='Sollar Array Mass')
        self.add_output('P_sa', units='W', desc='Sollar Array Power')

        self.declare_partials('*','*')

    def compute(self, inputs, outputs):
        eta_sa = inputs['eta_sa']
        G_sc = input['G_sc']
        A_sa = P_0/(eta_sa*G_sc*inputs['eta_EOL'])
        output['M_sa'] = A_sa*inputs['MAr']
        output['P_sa'] = G_sc*inputs['eta_degr']*eta_sa*A_sa
