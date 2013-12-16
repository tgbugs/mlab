#!/usr/bin/env python3.3
import pylab as plt
import numpy as np

x=np.arange(40)
y=np.cos(x)
plt.plot(x,y)
plt.plot([10,20],[10]*2,'b-',linewidth=10)

plt.show()

