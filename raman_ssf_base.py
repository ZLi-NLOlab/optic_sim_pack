import optic_sim_pack as osp
import numpy as np 
import matplotlib.pyplot as plt 
import sim_config_file as config

if __name__ == '__main__':
    import osp_param_file_generator as ofg

from functools import partial
from matplotlib import rcParams
rcParams['lines.linewidth'] = .8
rcParams['font.size'] = 8
fftshift = np.fft.fftshift

new_s_processing = config.new_s_processing 
new_p_processing = config.new_p_processing
new_c_processing = config.new_c_processing

# """-----------------------------------------------------------"""

# """ sim class initialisation """

sim_class = osp.ssf_sim_class(
    params= config.params, 
    E_init= config.E_init, 
    E_in_prof= config.E_in_prof,
    plotting= config.plotting_status, 
    saving= config.saving_status, 
    force_proc= config.force_proc_status 
    )

# """ initial launch config """ 

sim_class.saving_processing = partial(new_s_processing, sim_class)
sim_class.plotting_processing = partial(new_p_processing, sim_class)
sim_class.common_processing = partial(new_c_processing, sim_class)

config.sim_class_prelaunch_proc(sim_class)

plt.pause(.1)

try:
    sim_class.integration()
except RuntimeError:
    pass

plt.close(sim_class.figure)
# plt.show()
