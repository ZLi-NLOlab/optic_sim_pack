import numpy as np 

from optic_sim_pack import ssf_sim_useful_func as uf 
from optic_sim_pack import ssf_sim_save_default as sd

from math import factorial
from functools import partial, partialmethod
from scipy.interpolate import interp1d 

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

def dispersion_calc(params, f_sample):
    betak = params['betak']
    dispersion = 0 
    for n in betak.keys():
        if n <= params['order']:
            dispersion += f_sample**n / factorial(n) * betak[n]
    dispersion = 1j*params['L'] * (dispersion - f_sample * params['d'])
    return dispersion

"""-----------------------------------------------------------"""
def new_s_processing(class_obj):
    print('\r' + str(class_obj.rt_counter) + '    ', end = '')
    if class_obj.rt_counter > class_obj.m_rt:
        print('Exit loop')
        raise RuntimeError
    else:
        pass 

"""-----------------------------------------------------------"""
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
    text_temp = 'Duration = {:.2f} fs, P_max = {:.2f}, d1 = {:.3f}, Delta = {:.2f} ({:.4f}), RT = {}, peak_pos = {:.2f}'
    class_obj.text.set_text(text_temp.
    format(delta_t, 
    np.max(abE_temp), 
    class_obj.params['d'] * 1e15,
    class_obj.params_list[1]/class_obj.params['alpha'],  
    class_obj.params_list[1], 
    class_obj.rt_counter,
    (np.where(abE_temp == np.max(abE_temp))[0][0]- class_obj.params['npt']//2))) 

"""-----------------------------------------------------------"""
def new_c_processing(class_obj):
    pass 
    # class_obj.params_list[1] += 10*params['alpha']/10e3

    # incre_rt = 2000; save_size = 100 
    # if class_obj.rt_counter % incre_rt == 0:
    #     print('d incred, {}'.format(class_obj.rt_counter))
    #     class_obj.saving = False
    #     class_obj.params['d'] += .1e-15
    #     class_obj.params_list[6] = dispersion_calc(class_obj.params, class_obj.f_sample)

    # if (class_obj.rt_counter + save_size) % incre_rt == 0:
    #     print('Save started, {}'.format(class_obj.rt_counter))
    #     class_obj.saving = True 
        
    # if class_obj.saving and not class_obj.save_started:
    #     print('save started')
    #     class_obj.save_start()

    # if (np.max(np.abs(class_obj.E)**2) < 400) and not class_obj.saving:
    #     class_obj.saving = False
    #     print('sol died')
    #     raise RuntimeError

    # f_sN = 150; s_sN = class_obj.params['M_N'][0] - class_obj.params['S_P'][0] * 2500
    # if class_obj.saving != True:
    #     if class_obj.rt_counter == f_sN:
    #         print('saving initiated')
    #         class_obj.saving = True
    #     if class_obj.rt_counter >= s_sN: 
    #         print('saving initiated')
    #         class_obj.saving = True      
    # elif class_obj.rt_counter == (f_sN + int(class_obj.params['S_P'][0])):
    #     print('saving terminated')
    #     class_obj.saving = False 
    # if class_obj.saving and not class_obj.save_started:
    #     print('save started')
    #     class_obj.save_start()

"""-----------------------------------------------------------"""
from load_save_func import load

def sim_class_launch_params_return():
    params = params = load('raman_sim_params', extension = '.params')

    E =  (np.random.rand(params['npt']) + 1j * np.random.rand(params['npt'])) * 1e-12
    # E = uf.stack_load('raman_sol_init')[-1][-1]
    # E = np.exp(-((np.arange(params['npt']) - params['npt']//2 - 50)/(150e-15/(params['tspan']/params['npt'])))**2) * 22
    # E = uf.stack_load('759b1a_ssf_save_0')[0, :]

    prof = lambda t_sample: (np.exp(-((t_sample)/params['p_in_dur'])**2)) 

    return (params, E, prof)

"""-----------------------------------------------------------"""
from optic_sim_pack import ssf_sim_raman_aux as ra
import phase_matching_aux as pa
fftshift = np.fft.fftshift

def sim_class_prelaunch_proc(sim_class):
    """ misc params setup """
    sim_class.m_rt = sim_class.params['M_N'][0]

    """ group delay, phase mismatch calc"""
    delta_phi = pa.delta_phi_calc(sim_class.params, fftshift(sim_class.f_sample))
    delta_g = pa.delta_g_calc(sim_class.params, fftshift(sim_class.f_sample))
    zero_crossp = find_zero(delta_phi)
    zero_crossg = find_zero(delta_g)
    # print(sim_class.f_sample[zero_crossg]/2/np.pi)

    if len(zero_crossg) > 0:
        tau1p = fftshift(sim_class.f_sample)[zero_crossg[0]]
    else: 
        tau1p = 12.2e-15

    """ raman """
    tau1, tau2 = sim_class.params['RR_tau']
    sim_class.Raman_res_interp = lambda f_plot: ra.Raman_res_interp(f_plot, 
    Raman_mod= ra.Raman_res_SigDamped(*sim_class.params['RR_tau']))

    RR_ori = (ra.Raman_res_interp(sim_class.f_plot, 
    Raman_mod = ra.Raman_res_SigDamped()))

    sim_class.integ_param_const()
    RR = sim_class.params_list[5]
    
    def array_out(class_obj):
        return [class_obj.rt_counter, class_obj.params['d'], class_obj.E] 
    sim_class.save_update = partial(sd.save_update, sim_class, out_array_func = array_out)

    """ fig construct """
    sim_class.fig_constructor()
    sim_class.axp = sim_class.ax1.twinx() 
    sim_class.axp.plot(sim_class.t_sample, np.abs(sim_class.E_in)**2, c = 'red')
    sim_class.ax1.set_xlim(-10e-12, 20e-12)
    sim_class.ax1.set_ylim(-.05, 10)
    sim_class.text = sim_class.ax1.annotate('', xy = (.98, .98), xycoords = 'axes fraction', va = 'top', ha = 'right')
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

    sim_class.canvas.draw()
    sim_class.bg1 = sim_class.canvas.copy_from_bbox(sim_class.ax1.bbox)
    sim_class.bg2 = sim_class.canvas.copy_from_bbox(sim_class.ax2.bbox)


"""-----------------------------------------------------------"""
# param_list = load('various_length_params')
# def varying_param_proc(class_obj, N):
#     params_temp = param_list[N]
#     for key_temp in class_obj.params.keys():
#         if key_temp in ['M_N', 'S_P', 'RR_tau']:
#             continue 
        
#         if class_obj.params[key_temp] != params_temp[key_temp]:
#             print(key_temp, end = ' ')
#             class_obj.params[key_temp] = params_temp[key_temp]

#     if params_temp['L'] == .5:
#         class_obj.params['d'] += 13.5e-15
#     elif params_temp['L'] == 1:
#         class_obj.params['d'] += 6.5e-15
#     elif params_temp['L'] == 1.5:
#         class_obj.params['d'] += 3.5e-15
#     elif params_temp['L'] == 2:
#         class_obj.params['d'] += 1.5e-15
#     elif params_temp['L'] == 2.5:
#         class_obj.params['d'] += .5e-15
#     elif params_temp['L'] == 3:
#         class_obj.params['d'] += .2e-15

#     class_obj.E_init = params_temp['E_map']
#     class_obj.grid_constructor()
#     print(len(class_obj.E_init), len(class_obj.f_sample), class_obj.params['npt'])

#     print('L = {} started '.format(class_obj.params['L']))










