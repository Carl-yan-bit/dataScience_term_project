import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import math
from scipy.stats import norm
import scipy.stats


def fun(x, a, b, c):
    return a*np.exp(-(x-b)**2/(2*c**2))


def dic2int(dic):
    return int(dic['top_num'].replace(",",""))


num = []
with open('num.json', 'r') as f:
    num = json.load(f)


num=np.array(num)
mu=np.mean(num)
s=np.var(num)
sq=math.sqrt(s)
index=0
for i in range(len(num)):
    if(num[i] >mu+3*sq):
        index+=1

num=np.log(num[index:]+4388)
skewp=scipy.stats.skew(num)
kurtosisp=scipy.stats.kurtosis(num,fisher=False)
s1=np.sqrt(6*(len(num)-2)/((len(num)+1)*(len(num)+3)))
s2=np.sqrt(24*(len(num))*(len(num)-2)*(len(num)-3)/((len(num)+1)*(len(num)+1)*(len(num)+3)*(len(num)+5)))
u2=3-6/(len(num)+1)
t1=skewp/s1
t2=(kurtosisp-u2)/s2

fig=plt.figure()
n,bins,patches=plt.hist(num,bins=30,density=True)
binp=[]
for i in range(0,30):
    binp.append((bins[i]+bins[i+1])/2)
popt, _ =curve_fit(fun,binp,n,p0=[1,10.590104,0.492912],maxfev=5000000)
plt.plot(binp,fun(binp,popt[0],popt[1],popt[2]))
plt.hist(num,bins=30,density=True)
plt.show()