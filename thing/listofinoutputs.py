        #Propellant Mass
        self.add_input("DV_tot",units="m/s",desc='Total Delta V for the Orbit Maneauvre')
        self.add_input("v_e", units="m/s",desc='Exhaust Velocity')
        self.add_input("M_0", units="kg",desc='Total Initial Mass')
        self.add_output("M_p", units="kg",desc='Total Propellant Mass')

        #Radius Iter
        self.add_input('Ri',units='m',desc='Orbit Radius at beginning of timestep')
        self.add_output('Re',units='m',desc='Orbit Radius at end of timestep')
        self.add_input('Ti',units='N',desc='Satellite Thrust at beginning of timestep')
        self.add_input('Mi',units='kg',desc='Satellite Mass at beginning of timestep')

        #Solar Array
        self.add_input("A_sa", units='m**2', desc='Solar Array Area')
        self.add_input("G_sc", units='W/m**2', desc='Solar Flux Constant')
        self.add_input("eta_sa", units=None, desc='Solar Array Conversion Efficiency')
        self.add_input("Z_sa", units='kg/m**2', desc='Solar Array Mass-Area Ratio')
        self.add_output("P_sa", units='W', desc='Solar Array Power')
        self.add_output("M_sa", units='kg', desc='Solar Array Mass')

        #Battery
        #Mass inputs
        self.add_input('M_sa', units='kg', desc='Sollar Array Mass')
        self.add_input('M_0', units='kg', desc='Initial Mass')
        self.add_input('M_u', units='kg', desc='Payload Mass')
        self.add_input('M_ps', units='kg', desc='Propulsion System Mass')
        self.add_input("M_p", units="kg",desc='Total Propellant Mass')
        #Battery Inputs
        self.add_input('E_sp', units='J/kg', desc='Battery Specific Energy')
        self.add_input('P_req', units='W', desc='Baseline Required Power')
        self.add_input('eta_dis', units=None, desc='Discharge Efficiency')
        self.add_input('P_th', units='W', desc='Required Power for Thrust')
        self.add_input('P_sa', units='W', desc='Solar Array Power')
        #output
        self.add_output('M_batt', units='kg', desc='Battery Mass')
        self.add_output('T_ch', units='s', desc='Cycle Time of one charge phase')
        self.add_output('T_th', units='s', desc='Cycle Time of one thrust phase')


        #Constants
        self.add_input('mu', units='m**3/s**2', desc='Gravitational Parameter Central Body', val=(398600.4418*10**9))
