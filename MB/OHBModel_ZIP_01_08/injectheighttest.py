from math import log
t_trans = 90. * 24 * 3600
P_el = 2500.
M_dry = 1000.

I_sp = 1000.
eta_th = 0.42
g_0 = 9.81
mu = 3.986*10**14
R_E = 6371
h_f = 23000.

V_e = I_sp * g_0
F = 2. * eta_th * P_el / V_e
M_p = F * t_trans / V_e
M_0 = M_dry + M_p
DV = V_e * log(M_p / M_dry + 1)
def R_inj(x):
    return mu / (x + (mu / (h_f+R_E)) ** .5) ** 2 - R_E
print(f'{R_inj(DV)} and {R_inj(DV/1000)}')