#!/usr/bin/env python3.3
import pylab as plt
import numpy as np

x=np.arange(40)
y=np.cos(x)
yerr=np.random.uniform(0,1,40)
plt.figure()
#plt.plot(x,y)
#plt.plot([10,20],[10]*2,'b-',linewidth=10)
plt.errorbar(x,y,yerr=yerr,fmt='bo',capsize=5)

#plt.show()
plt.savefig('/tmp/testing_led.png')

