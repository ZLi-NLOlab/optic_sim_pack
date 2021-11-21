import optic_sim_pack as osp
import numpy as np 
import matplotlib.pyplot as plt 
import sim_processing_mod as spm

if __name__ == '__main__':
    import osp_param_file_generator as ofg

from functools import partial
from matplotlib import rcParams
rcParams['lines.linewidth'] = .8
rcParams['font.size'] = 8
fftshift = np.fft.fftshift

new_s_processing = spm.new_s_processing 
new_p_processing = spm.new_p_processing
new_c_processing = spm.new_c_processing

"""-----------------------------------------------------------"""

""" sim class generation """
params, E, prof_func = spm.sim_class_launch_params_return()

sim_class = osp.ssf_sim_class(params= params, E_init= E, 
plotting = True, saving = False , force_proc = False )

""" initial launch config """ 

prof = prof_func(sim_class.t_sample)
sim_class.E_in = sim_class.E_in * prof/max(prof) 

sim_class.saving_processing = partial(new_s_processing, sim_class)
sim_class.plotting_processing = partial(new_p_processing, sim_class)
sim_class.common_processing = partial(new_c_processing, sim_class)

spm.sim_class_prelaunch_proc(sim_class)

plt.pause(.1)

try:
    sim_class.integration()
except RuntimeError:
    pass

plt.close(sim_class.figure)
# plt.show()
