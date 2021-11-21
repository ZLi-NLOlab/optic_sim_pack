import optic_sim_pack as osp
import numpy as np 
import matplotlib.pyplot as plt 
import raman_aux as ra
import phase_matching_aux as pa
import sim_processing_mod as spm

if __name__ == '__main__':
    import osp_param_file_generator as ofg

from scipy.interpolate import interp1d
from optic_sim_pack import ssf_sim_useful_func as uf
from functools import partial
from load_save_func import load
from matplotlib import rcParams
rcParams['lines.linewidth'] = .8
rcParams['font.size'] = 8
fftshift = np.fft.fftshift

new_s_processing = spm.new_s_processing 
new_p_processing = spm.new_p_processing
new_c_processing = spm.new_c_processing

find_zero = spm.find_zero
norm_to_one = spm.norm_to_one
"""-----------------------------------------------------------"""

params = load('raman_sim_params', extension = '.params')
dur = params['p_in_dur']

E =  (np.random.rand(params['npt']) + 1j * np.random.rand(params['npt'])) * 1e-12
# E = uf.stack_load('raman_sol_init')[-1][-1]
# E = np.exp(-((np.arange(params['npt']) - params['npt']//2 - 50)/(150e-15/(params['tspan']/params['npt'])))**2) * 22
# E = uf.stack_load('759b1a_ssf_save_0')[0, :]

sim_class = osp.ssf_sim_class(params= params, E_init= E, 
plotting = True, saving = False , force_proc = False )

""" initial processing, not varied in loop """ 
sim_class.m_rt = params['M_N'][0]

sim_class.saving_processing = partial(new_s_processing, sim_class)
sim_class.plotting_processing = partial(new_p_processing, sim_class)
sim_class.common_processing = partial(new_c_processing, sim_class)

RR_ori = (ra.Raman_res_interp(sim_class.f_plot, 
Raman_mod = ra.Raman_res_SigDamped()))

shift = 0
prof = (np.exp(-((sim_class.t_sample - shift)/dur)**2)) 
sim_class.E_in = sim_class.E_in * prof/max(prof) 

sim_class.integ_param_const()
delta_phi = pa.delta_phi_calc(params, fftshift(sim_class.f_sample))
delta_g = pa.delta_g_calc(params, fftshift(sim_class.f_sample))
zero_crossp = find_zero(delta_phi)
zero_crossg = find_zero(delta_g)
print(sim_class.f_sample[zero_crossg]/2/np.pi)

if len(zero_crossg) > 0:
    tau1p = fftshift(sim_class.f_sample)[zero_crossg[0]]
else: 
    tau1p = 12.2e-15

tau1 = 12.2e-15 ; tau2 = 32e-15 
RR = sim_class.params_list[5] = fftshift(ra.Raman_res_interp(sim_class.f_plot, 
Raman_mod = ra.Raman_res_SigDamped(tau1 = tau1, tau2 = tau2)))
sim_class.params['RR'] = (tau1, tau2)

sim_class.fig_constructor()
sim_class.axp = sim_class.ax1.twinx() 
sim_class.axp.plot(sim_class.t_sample, np.abs(sim_class.E_in)**2, c = 'red')
sim_class.axp.axvline(shift, ls = '--')
sim_class.ax1.set_xlim(-10e-12, 20e-12)
sim_class.ax1.set_ylim(-.05, 10)
sim_class.text = sim_class.ax1.annotate('', xy = (.5, .8), xycoords = 'axes fraction')
sim_class.text.set_animated(True)
sim_class.animated_list.append((sim_class.ax1, sim_class.text))

sim_class.axa = sim_class.ax2.twinx()
sim_class.axa.plot(sim_class.lam_grid, norm_to_one(fftshift(RR.imag)), c = 'C2', label = 'RR')
sim_class.axa.plot(sim_class.lam_grid, norm_to_one(RR_ori.imag), '--', c = 'red', label = 'ori_RR')
sim_class.axa.plot(sim_class.lam_grid, norm_to_one(delta_phi) * 100, c = 'C1', label = 'delta_phi')
sim_class.axa.axhline(0, ls = '--', c = 'red')
sim_class.axa.axvline(1564.5221, ls = '--', c = 'green')
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

try:
    sim_class.integration()
except RuntimeError:
    pass

plt.close(sim_class.figure)
# plt.show()
