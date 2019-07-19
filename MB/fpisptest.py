from interpolate import csv_ip1d
path = 'Data/FP_Isp-Graph.csv'
f = csv_ip1d(path)
print(f(2850))
