import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

x = np.linspace(0,10000,20000)
y1 = stats.gamma.pdf(x, a=2, scale=400)
plt.plot(x, y1)
plt.show()

input()