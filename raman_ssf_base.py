import optic_sim_pack as osp
import numpy as np 
import matplotlib.pyplot as plt 
import raman_aux as ra
import phase_matching_aux as pa

if __name__ == '__main__':
    import osp_param_file_generator as ofg

from time import time as time 
from functools import partial
from load_save_func import load
from matplotlib import rcParams
rcParams['lines.linewidth'] = .8
rcParams['font.size'] = 8

def find_zero(arr):
    z_cross = []
    for n in range(len(arr) -1):
        if np.sign(arr[n] * arr[n+1]) == -1:
            z_cross.append(n)
    return z_cross

def norm_to_one(arr):
    span = (np.max(arr) - np.min(arr))
    return (arr)/span

params = load('raman_sim_params', extension = '.params')
dur = params['p_in_dur']

E = (np.random.rand(params['npt']) + 1j * np.random.rand(params['npt'])) * 1e-12 

sim_class = osp.ssf_sim_class(params= params, E_init= E, 
plotting = True, saving = False)
shift = 0
sim_class.E_in = sim_class.E_in * np.exp(-((sim_class.t_sample - shift)/dur)**2) 
sim_class.integ_param_const()
tau1 = 12.2e-15/1.3 ; tau2 = 32e-15 
RR = sim_class.params_list[5] = np.fft.fftshift(ra.Raman_res_interp(sim_class.f_plot, 
Raman_mod = ra.Raman_res_SigDamped(tau1 = tau1, tau2 = tau2)))

RR_ori = (ra.Raman_res_interp(sim_class.f_plot, 
Raman_mod = ra.Raman_res_SigDamped(tau1 = 12.2e-15, tau2 =  32e-15 )))

sim_class.axp = sim_class.ax1.twinx() 
sim_class.axp.plot(sim_class.t_sample, np.abs(sim_class.E_in)**2, c = 'red')
sim_class.axp.axvline(shift, ls = '--')
sim_class.ax1.set_xlim(-10e-12, 20e-12)
sim_class.ax1.set_ylim(-.5, 20)

delta_phi = pa.delta_phi_calc(params, np.fft.fftshift(sim_class.f_sample))
delta_g = pa.delta_g_calc(params, np.fft.fftshift(sim_class.f_sample))
zero_crossp = find_zero(delta_phi)
zero_crossg = find_zero(delta_g)

sim_class.axa = sim_class.ax2.twinx()
sim_class.axa.plot(sim_class.lam_grid, norm_to_one(np.fft.fftshift(RR.imag)), c = 'C2', label = 'RR')
sim_class.axa.plot(sim_class.lam_grid, norm_to_one(RR_ori.imag), '--', c = 'red', label = 'ori_RR')
sim_class.axa.plot(sim_class.lam_grid, norm_to_one(delta_phi) * 100, c = 'C1', label = 'delta_phi')
sim_class.axa.axhline(0, ls = '--', c = 'red')
sim_class.axa.plot(sim_class.lam_grid, norm_to_one(delta_g) * 50, c = 'C4', label = 'delta_g')
for n in zero_crossg:
    sim_class.axa.axvline(sim_class.lam_grid[n], ls = '--')
for n in zero_crossp:
    sim_class.axa.axvline(sim_class.lam_grid[n], ls = '-.', c = 'C1')

sim_class.axa.legend(loc = 1)

sim_class.axa.set_ylim(-.7, .7)
plt.pause(.1)
sim_class.bg1 = sim_class.canvas.copy_from_bbox(sim_class.ax1.bbox)
sim_class.bg2 = sim_class.canvas.copy_from_bbox(sim_class.ax2.bbox)

sim_class.m_rt = 1e4

def new_processing(class_obj):
    if class_obj.rt_counter > class_obj.m_rt:
        exit()
    else:
        pass 

def new_processing2(class_obj):
    print(class_obj.rt_counter)

sim_class.saving_processing = partial(new_processing, sim_class)
sim_class.plotting_processing = partial(new_processing2, sim_class)

start = time()
sim_class.integration()

print(time() - start)