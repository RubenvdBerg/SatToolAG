import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from csv import reader
from numpy import array, exp, arange


def csv_ip1d(path,graph=False,bounds=False,switch=False):
    '''Opens csv file and converts the data to an interpolated line fucntion.
    CSV file needs to be two comma separated columns of X and Y data without headers or (empty) strings

    path    = pathstring                                    (Example: 'Data/datafile.csv')
    param   = list of first guesses for paramaters a,b,..   (Example: [1.0,0.1,0.8])
    grap    = if True returns graph of the datapoint and approximated curve
    bounds  = if True returns boundaries of the interpolated function as well as the function
    switch  = if True plots x-values as y and vice versa
    '''
    with open(path) as csvfile:
        dataset = reader(csvfile)
        Data = [[],[]]
        for i in dataset:
            Data[0].append(i[0])
            Data[1].append(i[1])
    DataX = array([float(i) for i in Data[0]])
    DataY = array([float(i) for i in Data[1]])
    if switch == True:
        DataX, DataY = DataY, DataX
    function = interp1d(DataX,DataY)

    if graph == True:
        xnew = arange(DataX[0],DataX[-1],1)
        ynew = function(xnew)
        plt.plot(DataX,DataY,'o',xnew,ynew,'-')
        plt.show()

    if bounds ==  True:
        return function, [DataX[0],DataX[-1]]
    if bounds == False:
        return function

if __name__ == '__main__':
    Rinject = 13369
    RIfunc, rbounds  = csv_ip1d('Data/InjectHeight.csv', switch=True, bounds=True)
    IMfunc, bounds  = csv_ip1d('Data/SepMass.csv', bounds=True)
    print(rbounds)
    print(RIfunc(Rinject), bounds)
    Msep    = IMfunc(RIfunc(Rinject))
    print(Msep)
