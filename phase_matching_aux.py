import matplotlib.pyplot as plt 
import numpy as np 

from load_save_func import load 
from math import factorial

c = 3e8

def CW_return(del0, alpha, X, gamma, L):
    Delta = del0/alpha
    roots = np.roots([1, -2*Delta, 1+Delta**2, -X])
    root = []
    for n_temp in roots:
        if np.imag(n_temp) == 0:
            root.append(n_temp)

    sol_min = (min(root) * (1/(np.sqrt(gamma * L/alpha)))**2).real
    sol_max = (max(root) * (1/(np.sqrt(gamma * L/alpha)))**2).real
    return sol_min

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
    



