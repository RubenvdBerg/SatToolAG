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

        output[''] =
