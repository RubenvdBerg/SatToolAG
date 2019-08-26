import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from csv import reader
from numpy import array, exp, arange, linspace


def csvtocurve(func,path,param=None,graph=False,givepopt=False):
    '''Returns function that approximates the csv data in the given path for a given function transform,
    CSV file needs to be two comma separated columns of X and Y data without headers or (empty) strings.

    func    = function form                                 (Example: lambda x,a,b: a*x+b)
    path    = pathstring                                    (Example: 'Data/datafile.csv')
    param   = list of first guesses for paramaters a,b,..   (Example: [1.0,0.1,0.8])
    grap    = if True returns graph of the datapoints and approximated curve as well as R2 value
    givepopt= if True returns function as well as list of optimal parameters
    '''

    csvfile = open(path)
    dataset = reader(csvfile)
    Data = [[],[]]
    for i in dataset:
        Data[0].append(i[0])
        Data[1].append(i[1])
    DataX = array([float(i) for i in Data[0]])
    DataY = array([float(i) for i in Data[1]])
    if param != None:
        popt, pcov = curve_fit(func,DataX,DataY, p0=param)
    popt, pcov = curve_fit(func,DataX,DataY)

    if graph == True:
        xnew = linspace(DataX[0],DataX[-1],100)
        ynew = func(xnew,*popt)
        plt.plot(DataX,DataY,'o',xnew,ynew,'-')
        plt.show()
        yaverage = sum(DataY)/len(DataY)
        SStot = 0
        SSres = 0
        fnew = func(DataX,*popt)
        for y, f in zip(DataY,fnew):
            SStot += (y-yaverage)**2
            SSres += (y-f)**2

        R2 = 1-SSres/SStot
        print(f'R2 is {R2}')
    if  givepopt == True:
        return lambda x : func(x,*popt), popt
    elif givepopt == False:
        return lambda x : func(x,*popt)

if __name__ == '__main__':
    print('Hi')

    # f = lambda x,a,b,c,d: a+b*x+c*x**2+d*x**3

    f = lambda x,a,b,c,d,e : a+b*x+c*x**2+d*x**3+e*x**4
    func, popt = csvtocurve(f,'Data/Launchers/Ariane64.csv',graph=True,givepopt=True)
    print(popt)
    # f = lambda x,a,b,c,d,e,f: a+b*x+c*x**2+d*x**3+e*x**4+f*x**5
    # popt = csvtocurve(f,'Data/InjectionHeight.csv')
    #
    # def injectheight(Isp):
    #     return f(Isp,*popt)
    #
    # f2 = lambda x,a,b : a*x**b
    # popt2 = csvtocurve(f2,'Data/SeparationMass.csv')
    # def sepmass(Isp):
    #     return f2(Isp,*popt2)

    # f3 = lambda x,a,b,c,d,e,f,g,h: a+b*x+c*x**2+d*x**3+e*x**4+f*x**5+g*x**6+h*x**7
    # popt3 = csvtocurve(f3,'Data/TransferEfficiency.csv',)
    # def transeff(Isp):
    #     return f(Isp,*popt3)
    # f = lambda x,a,b,c,d,e: a*exp(-b*x)+c*exp(-d*x)+e
    # def f(x,a,b,c,d,e,f,g):
    #     return a*exp(-b*x)+c*exp(-d*x)+e+f*x+g*x**2
