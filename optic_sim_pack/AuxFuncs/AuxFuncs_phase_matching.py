import numpy as np 

from .AuxFuncs_misc_func import CW_return
from math import factorial

c = 3e8


def delta_phi_calc(params, f_sample):
    betak = params['betak'] 
    X = params['P_in'] * params['gamma'] * params['L'] * params['theta1']/params['alpha']**3 
    CW_max = CW_return(params['del0'], params['alpha'], X, params['gamma'], params['L'])

    dphi = np.zeros(len(f_sample))
    for n in range(2, params['order'] + 1):
        dphi += betak[n] * params['L'] * f_sample**n/factorial(n)
    dphi += 2 * CW_max * params['gamma'] * params['L'] - params['del0'] - params['d'] * f_sample

    return dphi

def delta_g_calc(params, f_sample):
    betak = params['betak']
    dphi = np.zeros(len(f_sample))
    for n in range(2, params['order'] + 1):
        dphi += betak[n] * params['L'] * f_sample**(n-1)/factorial(n-1)
    dphi -= params['d'] * params['L']
    return dphi
    



