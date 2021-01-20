import json

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import math
import pandas as pd
import matplotlib.mlab as mlab
from scipy.stats import norm
from scipy.stats import t
import scipy.stats
import demjson

data=[]
with open('normal.json', 'r') as f:
    data = json.load(f)
list=[]
id=[]
data=sorted(data, key = lambda i: int(i['top_num'].replace(",","")),reverse=True)


result=[]
for i in range(0,845):
    result.append(data[i])
    print(data[i]['url'])
    print(data[i]['top_num'])
    print("\n")
with open('result.json','w') as f:
    json.dump(result,f)
print(max)