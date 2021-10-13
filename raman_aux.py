import numpy as np 

from functools import partial 
from numpy.fft import ifft, fft, fftshift 
from scipy.interpolate import interp1d


vp = {
        1: {'cP': 56.25, 'ci': 1, 'gf': 52, 'lf': 17.37},
        2: {'cP': 100, 'ci': 11.40, 'gf': 110.42, 'lf': 38.81},  
        3: {'cP': 231.25, 'ci': 36.67, 'gf': 175, 'lf': 58.33},
        4: {'cP': 362.5, 'ci': 67.67, 'gf': 162, 'lf': 54.17},
        5: {'cP': 463, 'ci': 74, 'gf': 135.33, 'lf': 45.11},
        6: {'cP': 497, 'ci': 4.5, 'gf': 24.5, 'lf': 8.17},
        7: {'cP': 611.5, 'ci': 6.8, 'gf': 41.5, 'lf': 13.83},
        8: {'cP': 691.67, 'ci': 4.6, 'gf': 155, 'lf': 51.67},
        9: {'cP': 793.67, 'ci': 4.2, 'gf': 59.5, 'lf': 19.83},
        10: {'cP': 835.5, 'ci': 4.5, 'gf': 64.3, 'lf': 21.43},
        11: {'cP': 930, 'ci': 2.7, 'gf': 150, 'lf': 50},
        12: {'cP': 1080, 'ci': 3.1, 'gf': 91, 'lf': 30.33},
        13: {'cP': 1215, 'ci': 3, 'gf': 160, 'lf': 53.33}}

c = 299792458

def interpol_aux(RR_f, f_ori, f_fit):
    RR_fR = interp1d(f_ori, RR_f.real, kind = 'cubic')
    RR_fI = interp1d(f_ori, RR_f.imag, kind = 'cubic')

    RR_fitR = RR_fR(f_fit)
    RR_fitI = RR_fI(f_fit)

    return RR_fitR + 1j * RR_fitI

def Raman_res_SigDamped_base(t_sample, tau1, tau2):
    "NOT FOR USE IN SIMULATION"
    "Single dampled oscillator model, tau1 gain peak position, tau2 gain bandwidth"

    hr = np.exp(-t_sample/tau2)*np.sin(t_sample/tau1) * np.heaviside(t_sample, 1) 
    
    return hr 

def Raman_res_SigDamped(tau1 = 12.2e-15, tau2 = 32e-15):
        return lambda x: Raman_res_SigDamped_base(x, tau1, tau2)

def Raman_res_multiV_base(t_sample): 
    "NOT FOR USE IN SIMULATION"
    "Multi-vibrational mode model"
    key_list = vp.keys()
    
    if type(t_sample) == int:
        hr = 0
    else :
        hr = np.zeros(len(t_sample))
    
    for key in key_list:
        p = vp[key]
        cp = p['cP'] * 1e2 * 2 * np.pi * c
        gf = p['gf'] * 1e2 * np.pi * c
        lf = p['lf'] * 1e2 * np.pi * c
        hr_temp = p['ci'] * np.exp(-lf * t_sample) * np.exp(- (gf * t_sample/2)**2) * np.sin(cp * t_sample) * np.heaviside(t_sample, 1)
        
        hr += hr_temp
    return hr

def Raman_res_multiV():
    return Raman_res_multiV_base

def Raman_res_interp(f_fit, npt_interpol = 2**14, Raman_mod = Raman_res_multiV):
    npt = npt_interpol
    tspan =  3000 * 1e-15 

    if .5 * npt/tspan < max(f_fit):
        base = np.ceil(np.log2(max(f_fit)/tspan))
        npt = 2**base 
        print('base changed to {}'.format(base))
    else: pass 

    grid = np.linspace(-npt/2, npt/2, npt, endpoint = False)/npt 
    t_sample = grid * tspan
    f_sample = grid * npt/tspan 
    
    RR = Raman_mod(t_sample)
    RR_f = fftshift(ifft(fftshift(RR))) 
    RR_fit = interpol_aux(RR_f, f_sample, f_fit)
    RR_fit /= np.sum(fftshift(fft(fftshift(RR_fit)).real)) * 1/len(f_fit)

    return RR_fit


