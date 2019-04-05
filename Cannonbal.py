from openmdao.api import IndepVarComp, Problem, ExplicitComponent

class Cannonball(ExplicitComponent):

    def initialize(self):

        self.options.declare('delta_t', default=0.1)

    def setup(self):

        self.add_input('Yi', units='m',   desc='position at the start of the time-step')
        self.add_input('Vi', units='m/s', desc='velocity at the start of the time-step')

        self.add_output('Ye', units='m',   desc='position at the end of the time-step')
        self.add_output('Ve', units='m/s', desc='velocity at the end of the time-step')

        self.declare_partials(of='*', wrt='*', method='cs')


    def compute(self, inputs, outputs):

        dt = self.options['delta_t']

        outputs['Ve'] = 9.81 * dt + inputs['Vi']
        outputs['Ye'] = 0.5 * 9.81 * dt**2 + inputs['Vi'] * dt + inputs['Yi']


if __name__ == "__main__":
    import numpy as np
    import matplotlib.pylab as plt

    N_TIMES = 10

    p = Problem()

    ivc = p.model.add_subsystem('init_conditions', IndepVarComp(), promotes= ['*'])
    ivc.add_output('Y0', 100., units='m')
    ivc.add_output('V0', 0, units='m/s')

    for i in range(N_TIMES):
        p.model.add_subsystem(f't_{i}', Cannonball())


    for i in range(N_TIMES-1):
        p.model.connect(f't_{i}.Ye', f't_{i+1}.Yi')
        p.model.connect(f't_{i}.Ve', f't_{i+1}.Vi')

    p.model.connect('Y0', 't_0.Yi')
    p.model.connect('V0', 't_0.Vi')

    p.setup()

    p.run_model()


    # collect the data into an array for plotting
    Y = [p['Y0'],]
    V = [p['V0'],]
    for i in range(N_TIMES):
        Y.append(p[f't_{i}.Ye'])
        V.append(p[f't_{i}.Ve'])

    times = np.arange(N_TIMES+1) * .01 # delta_t

    fig, ax = plt.subplots()
    ax.plot(times, Y)
    ax.set_ylabel('velocity (m/s')
    ax.set_xlabel('time (s)')

    plt.show()
