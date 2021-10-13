import numpy as np 

from numpy.fft import fftshift, ifft, fft 
from scipy.interpolate import interp1d
from math import factorial

def grid_constructor(class_obj):
    """Temporal/spectral/wavelength grid constructor"""
    npt = class_obj.params['npt']
    t_span = class_obj.params['tspan']
    
    grid = np.linspace(-npt/2, npt/2, npt, endpoint = False)/npt 
    class_obj.t_sample = grid * t_span
    class_obj.f_plot = grid * npt/t_span
    """reverse freq_grid for integrator step"""
    class_obj.f_sample = fftshift(class_obj.f_plot* 2 *np.pi)
    if 'wl_pump' in class_obj.params:
        class_obj.lam_grid = c/(class_obj.f_plot + c/class_obj.params['wl_pump']) * 1e9
    else:
        class_obj.lam_grid = None 

def params_list_constructor(class_obj):
    params = class_obj.params
    f_sample = class_obj.f_sample
    """Raman response calculated with correct grid then shifted"""
    RR_f = fftshift(Raman_res_interp(fftshift(f_sample/2/np.pi)))
    h = 1/params['M_N'][1]

    betak = params['betak']
    dispersion = 0 
    for n in betak.keys():
        if n <= params['order']:
            dispersion += f_sample**n / factorial(n) * betak[n]
    dispersion = 1j*params['L'] * (dispersion - f_sample * params['d'])

    out_list = [params['alpha'],
                params['del0'],
                params['gamma'],
                params['L'],
                params['fR'],
                RR_f, dispersion, h
                ]

    return out_list

def CW_return(del0, alpha, P_in, gamma, L, theta):
    Delta = del0/alpha
    X = P_in * (gamma * L * theta)/alpha**3
    roots = np.roots([1, -2*Delta, 1+Delta**2, -X])
    root = []
    for n_temp in roots:
        if np.imag(n_temp) == 0:
            root.append(n_temp)

    sol_min = (min(root) * 1/(gamma * L/alpha)).real
    sol_max = (max(root) * 1/(gamma * L/alpha)).real

    return sol_min, sol_max

# =============================================================================
# raman response function (real unit)
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

def Raman_res(t_sample):
    "NOT FOR USE IN SIMULATION"
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

def Raman_res_interp(f_fit, npt_interpol = 2**14, return_sample = False):
    
    npt = npt_interpol
    grid = np.linspace(-npt/2, npt/2, npt, endpoint = False)/npt 
    tspan =  1500 * 2 * 1e-15 
    t_sample = grid * tspan
    f_sample = grid * npt/tspan 
    
    RR = Raman_res(t_sample)
    RR_f = fftshift(ifft(fftshift(RR))) 
    RR_fR = interp1d(f_sample, RR_f.real, kind = 'cubic')
    RR_fI = interp1d(f_sample, RR_f.imag, kind = 'cubic')
    
    RR_fitR = RR_fR(f_fit)
    RR_fitI = RR_fI(f_fit)
    RR_fit = RR_fitR + 1j * RR_fitI
    RR_fit /= np.sum(fftshift(fft(fftshift(RR_fit)).real)) * 1/len(f_fit)

    if return_sample:
        return f_sample, RR_f
    else: return RR_fit
    
# =============================================================================