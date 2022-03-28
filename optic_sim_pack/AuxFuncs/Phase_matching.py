import numpy as np 

from .Misc_func import cw_return
from math import factorial

c = 3e8

def delta_phi_calc(params):
    betak = params.betak 
    f_sample = params.f_plot * 2 * np.pi

    cw_min, cw_max = cw_return(params.del0, params.alpha, params.P_in, params.gamma, params.L, params.theta1)

    dphi = np.zeros(len(f_sample))
    for n in betak.keys():
        if n > params.order: break
        dphi += betak[n] * params.L * f_sample**n/factorial(n)
    dphi += 2 * cw_max * params.gamma* params.L - params.del0 - params.d * params.L * f_sample

    return dphi

def delta_g_calc(params):
    betak = params.betak
    f_sample = params.f_plot * 2 * np.pi

    dphi = np.zeros(len(f_sample))
    for n in betak.keys():
        if n > params.order: break
        dphi += betak[n] * params.L * f_sample**(n-1)/factorial(n-1)
    dphi -= params.d * params.L
    return dphi
    



