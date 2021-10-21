import optic_sim_pack as osp
import numpy as np 
import matplotlib.pyplot as plt 
import raman_aux as ra
import phase_matching_aux as pa

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

def find_zero(arr):
    z_cross = []
    for n in range(len(arr) -1):
        if np.sign(arr[n] * arr[n+1]) == -1:
            z_cross.append(n)
    return z_cross

def norm_to_one(arr):
    span = (np.max(arr) - np.min(arr))
    return (arr)/abs(span)

def l_interp(val, index_arr, arr):
    inte_temp = interp1d(arr[index_arr], index_arr)
    return inte_temp(val)

def new_s_processing(class_obj):
    if class_obj.rt_counter > class_obj.m_rt:
        print('Exit loop')
        raise RuntimeError
    else:
        pass 

def new_p_processing(class_obj):
    abE_temp = np.abs(class_obj.E)**2
    fwhm = uf.FWHM_find(np.max(abE_temp)/2, abE_temp)
    try:
        upper = l_interp(np.max(abE_temp)/2, [fwhm[1], fwhm[1]-1], abE_temp)
        lower = l_interp(np.max(abE_temp)/2, [fwhm[0], fwhm[0]+1], abE_temp)
    except ValueError:
        upper = fwhm[1]
        lower = fwhm[0]
    delta_t = (upper - lower) * (class_obj.t_sample[1] - class_obj.t_sample[0]) * 1e15 
    class_obj.text.set_text('Duration = {:.2f} fs, P_max = {:.2f}, Delta = {:.2f}, RT = {}, '.
    format(delta_t, np.max(abE_temp), class_obj.params_list[1]/class_obj.params['alpha'], class_obj.rt_counter)) 

def new_c_processing(class_obj):
    pass 
    class_obj.params_list[1] += 50*params['alpha']/10e3
    # if class_obj.saving != True:
    #     if class_obj.rt_counter >= 10e3:
    #         print('saving initiated')
    #         class_obj.saving = True 
             

params = load('raman_sim_params', extension = '.params')
dur = params['p_in_dur']

E = (np.random.rand(params['npt']) + 1j * np.random.rand(params['npt'])) * 1e-12
# E = np.exp(-((np.arange(params['npt']) - params['npt']//2 - 50)/(150e-15/(params['tspan']/params['npt'])))**2) * 22
# E = uf.stack_load('759b1a_ssf_save_0')[0, :]

sim_class = osp.ssf_sim_class(params= params, E_init= E, 
plotting = True, saving = False, force_proc = False )

""" initial processing, not varied in loop """ 
sim_class.m_rt = params['M_N'][0]

sim_class.saving_processing = partial(new_s_processing, sim_class)
sim_class.plotting_processing = partial(new_p_processing, sim_class)
sim_class.common_processing = partial(new_c_processing, sim_class)

RR_ori = (ra.Raman_res_interp(sim_class.f_plot, 
Raman_mod = ra.Raman_res_SigDamped(tau1 = 12.2e-15, tau2 = 32e-15 )))

shift = 0
prof = (np.exp(-((sim_class.t_sample - shift)/dur)**2)) #* 0 + 1
sim_class.E_in = sim_class.E_in * prof/max(prof) 

sim_class.integ_param_const()
delta_phi = pa.delta_phi_calc(params, fftshift(sim_class.f_sample))
delta_g = pa.delta_g_calc(params, fftshift(sim_class.f_sample))
zero_crossp = find_zero(delta_phi)
zero_crossg = find_zero(delta_g)

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
# sim_class.ax1.set_xlim(-10e-12, 20e-12)
sim_class.ax1.set_ylim(-.05, 10)
sim_class.text = sim_class.ax1.annotate('', xy = (.5, .8), xycoords = 'axes fraction')
sim_class.text.set_animated(True)
sim_class.animated_list.append((sim_class.ax1, sim_class.text))

sim_class.axa = sim_class.ax2.twinx()
sim_class.axa.plot(sim_class.lam_grid, norm_to_one(fftshift(RR.imag)), c = 'C2', label = 'RR')
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

try:
    # sim_class.save_start()
    sim_class.integration()
except RuntimeError:
    pass

plt.close(sim_class.figure)