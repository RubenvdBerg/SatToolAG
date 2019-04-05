from openmdao.api import ExplicitComponent

class XComp(ExplicitComponent):

    def setup(self):
        #input
        self.add_input()
        #independent variables
        self.add_input()
        #output
        self.add_output()

        self.declare_partials('*','*')

    def compute(self, inputs, outputs):

        outputs[''] = 1


from openmdao.api import ImplicitComponent

class XComp(ImplicitComponent):
    """"Does X"""

    def setup(self):
        #input
        self.add_input()
        #independent variables
        self.add_input()
        #output
        self.add_output()

        self.declare_partials('*','*', method='fd')

    def apply_nonlinear(self, inputs, outputs, residuals):

        residuals[''] = 1
