from math import asin,sqrt,pi
def GetDarkTime(R):
    """Calculates the length of time an object is in darkness in an equatorial circular orbit around the Earth with the given orbit radius in [meters]"""
    mu = 398600.*10**9
    R_E = 6371000.


    return 2*asin(R_E/R)*sqrt(R**3/mu)


def GetOrbitTime(R):
    """Calculates the orbital period of an equatorial circular orbit around the Earth with the given orbit radius in [meters]"""
    mu = 398600.*10**9
    return 2*pi*sqrt(R**3/mu)

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    print(GetDarkTime(7371000))
    print(GetOrbitTime(6371000)/3600)
    Rlist =[]
    Dlist = []
    for i in range(6371,42164):
        Rlist.append(i*1000.)
        Dlist.append(GetDarkTime(i*1000.))
    plt.plot(Rlist, Dlist)
    plt.show()
