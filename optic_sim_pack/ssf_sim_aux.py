import numpy as np 

from numpy.fft import fftshift, ifft, fft 
from scipy.interpolate import interp1d
from math import factorial

c = 3e8

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
    RR_f = fftshift(class_obj.Raman_res_interp(fftshift(f_sample/2/np.pi)))
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

def integration_step(self, E, E_in, alpha, del0, gamma, L, fr, RR_f, dispersion, h, N):
    """integrator step, performed in fftshifted grid"""
    for temp in range(N):
        abs_E = np.abs(E)**2

        RA = RR_f * ifft(abs_E)
        RA = fft(RA)

        NL = -alpha - 1j*del0 +  1j * gamma * L * ((1-fr) * abs_E + fr * RA)
        k0 = E + E_in/NL
        E_NL = k0* np.exp(NL*h) - E_in/NL

        E_f = ifft(E_NL)
        E_dispersion  = E_f * np.exp(dispersion*h)
        E = fft(E_dispersion)

    return E