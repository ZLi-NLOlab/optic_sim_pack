import optic_sim_pack as osp 
import numpy as np

import osp_param_file_generator
from matplotlib import rcParams, use
from load_save_func import load

# """define useful functions, namely, for initial E and E_in profile and absorption boundary"""
def E_prof_func(params_c):
    return np.exp(- params_c.t_sample**2/2e-12**2)

def E_init_func(params_c):
    N = 1
    tau = np.sqrt(N**2 * abs(params_c.betak[2])/params_c.gamma/params_c.P_in) 
    prof = 1/np.cosh(params_c.t_sample/tau)
    return np.sqrt(params_c.P_in) * prof

def absorption_boundary(t_sample, shift, edge, base, max_val = 1):
    y = np.tanh((t_sample + shift)/edge) - np.tanh((t_sample - shift)/edge)
    y = max_val - y * (max_val - base)/2
    return y

# """various modifiable processing calls"""
def int_manager_init_call(self):
    # self.plot_control.fig_vars.t_xlim = (-1e-11, 1e-11) 
    self.plot_control.fig_vars.t_ylim = (-.05, .5)

def pre_launch_call(self):
    ax = self.plot_control.fig_vars.twins[0]
    ax.cla()
    ax.plot(self.params_c.t_sample, self.params_c.alpha, c = 'C2', ls = '--')
    ax.set_ylim( 0 , max(self.params_c.alpha) * 1.1)
    self.plot_control.canvas_update()

def common_processing(self):
   pass 
    # if self.params_c.rt_counter == int(7e4):
    #     self.status_c.saving = True
    #     self.save_control.save_start()
    # if self.params_c.rt_counter == int(7e4 + self.params_c._S_intv):
    #     raise StopIteration

# """loading params, not necessary, one can define params directly"""
params = load('raman_sim_params', extension = '.params')

# """initialise the NumInt_class"""
sim_class = osp.NumInt_class(
        params, 
        E_in_prof= E_prof_func,
        E_init = E_init_func,
        plotting = True, saving = True,
        save_name = 'apple_sim',
        integration_method= 'LLE_ssf',
        int_init_call  = int_manager_init_call,
        pre_launch_call = pre_launch_call,
        common_proc_call = common_processing, 
        status_c_attri = {'tar_final': True, 'tar_remove': True}
    )

# """we can directly modify the alpha to implement absorption boundary""" 
params = sim_class.params_c
boundary = absorption_boundary(params.t_sample/(params.tspan/2), .8 , .1, params.alpha, .1)
sim_class.params_c.alpha = boundary

# """launching the numerical integration routine"""
sim_class.launch()



