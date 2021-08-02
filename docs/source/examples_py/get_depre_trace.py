
from icarus_nmr.mock_driver import Driver
driver = Driver()
driver.init()

depre = driver.get_depre_trace()

pre = driver.get_pre_trace()


import matplotlib.pyplot as plt
fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1)
ax1.plot(pre[5,:],'-',label = 'pressurization')
ax2.plot(depre[5,:],'-',label = 'depressurization')
ax1.legend()
ax2.legend()
