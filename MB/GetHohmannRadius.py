from openmdao.api import Group, Problem, NewtonSolver, ScipyKrylov
from implicit_radius import RadiusComp

def GetHohmannRadius(DV_i,R_i):
    """Function to get the final radius when given a initial radius and DeltaV (change)"""

    p = Problem()
    p.model = model = Group()
    model.add_subsystem('radiusconverge',RadiusComp(),promotes=['*'])
    model.nonlinear_solver = NewtonSolver(maxiter = 20, iprint= 0, atol =1e-10, rtol=1e-12)
    model.linear_solver = ScipyKrylov()
    p.setup()
    p['DeltaV'] = DV_i
    p['R_i'] = R_i
    p.run_model()
    return p['R_f']

if __name__ == '__main__':
    print(GetHohmannRadius(DV_i = 100 , R_i=6778000 ))
