import numpy as np 

from ...AuxFuncs import Raman_calc as rc
from numpy.fft import fft, ifft, fftshift
from math import factorial 

class numint_LLE_ikeda_class():

    def params_constructor(self):
        params = self.params_c
        f_sample = params.f_sample

        params.E_in_mag = np.sqrt(params.P_in * params.theta1)

        # """Raman response calculated with correct grid then shifted"""
        if 'RR_method' in params:
            if params.RR_method == 'multiV':
                raman_method = rc.raman_res_multiV
            elif params.RR_method == 'SigDamped':
                raman_method = rc.raman_res_SigDamped
            else:
                raise NotImplementedError('Raman method not found')
        else: 
            params.RR_method = 'multiV'
            raman_method = rc.raman_res_multiV

        
        params.RR_f = fftshift(
                rc.raman_res_interp(
                    fftshift(f_sample/2/np.pi), 
                    Raman_mod = raman_method(*params.RR_tau)
                    ))

        params.h = 1/params._N * params.L

        betak = params.betak
        dispersion = 0 
        for n in betak.keys():
            if n <= params.order:
                dispersion += f_sample**n / factorial(n) * betak[n]
        dispersion = 1j * (dispersion - f_sample * params.d)
        params.dispersion = dispersion

    def integration_step(self):
        params = self.params_c
        params.E = params.E * np.exp(-params.alpha) * np.exp(-1j * del0) + params.E_in_mag * params.E_in_prof

        for N_temp in range(params._N):
            abs_E = np.abs(params.E)**2
            
            RA = fft(params.RR_f * ifft(abs_E))
            
            NL = 1j * params.gamma * ((1-params.fR) * abs_E + params.fR * RA) * params.h
            E_NL = params.E * np.exp(NL)
            
            E_dispersion = ifft(E_NL) * np.exp(params.dispersion * params.h)
            params.E = fft(E_dispersion)

numint_LLE_ikeda_class.__name__ = 'LLE_Ikeda defualt'  