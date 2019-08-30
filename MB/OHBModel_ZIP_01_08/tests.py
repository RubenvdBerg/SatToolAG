import unittest
from OHBModel import OHBModel


class OHBModelTest(unittest.TestCase):
    def setUp(self):
        self.rangeoutputs = (
            OHBModel(
                i_sp=I_sp,
                p_sat=2500.,
                t_trans=90*24*3600.,
                m_dry=1000.,
                r_f=23222. * 10 ** 3,
                launcher='Ariane62'
            )
            for I_sp in range(260,3600,20)
        )
        self.simpledictionary = OHBModel(i_sp=2000, p_sat=2500., t_trans=90 * 24 * 3600., m_dry=1000., r_f=23222. * 10 ** 3, launcher='Ariane62', allvars=True)
    def test_simple_range_injectionheight(self):
        for outputs in self.rangeoutputs:
            r_inj, *_ = outputs
            self.assertTrue(400. <= r_inj <= 23222.)
    def test_constants(self):
        dictionary = self.simpledictionary
        self.assertEqual(dictionary['g0'], 9.81)
        self.assertEqual(dictionary['mu'], 3.98600*10**14)
        self.assertEqual(dictionary['R_E'], 6371.)
    def test_simple_separationmass(self):
        for outputs in self.rangeoutputs:
            _, m_sep, _ = outputs
            a62_max_mass = 10350.
            self.assertTrue(0. <= m_sep <= a62_max_mass)
    def test_simple_transferefficiency(self):
        for outputs in self.rangeoutputs:
            *_, t_eff = outputs
            self.assertTrue(0. <= t_eff)
    def test_consistency(self):
        print('todo')
        #test if r_inj changes for below 400 km
        # and not if r_inj before 400 km. consistency



if __name__ == '__main__':
    unittest.main()
