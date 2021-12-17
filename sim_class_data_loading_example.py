import numpy as np 
import matplotlib.pyplot as plt 
import optic_sim_pack as osp

from optic_sim_pack import AuxFuncs
from optic_sim_pack.AuxFuncs import load_save

data = AuxFuncs.load_save.tar_load_NumInt('apple_sim.simout.tar.gz.08d61c')

params = data['params']
E_data = data['data'][0][1]

fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

ax1.plot(np.abs(E_data)**2)
ax2.plot()

plt.show()
