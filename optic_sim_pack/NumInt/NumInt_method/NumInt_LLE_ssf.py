import numpy as np 

from ...AuxFuncs import Raman_calc as rc
from numpy.fft import fft, ifft, fftshift
from functools import partial
from math import factorial 

class NumInt_LLE_ssf_class():

    def integration_step(self):
        """integrator for LLE using ssf, performed in fftshifted grid"""
        params = self.params_c
        for temp in range(params._N):
            abs_E = np.abs(params.E)**2

            RA = params.RR_f * ifft(abs_E)
            RA = fft(RA)

            NL = -params.alpha - 1j*params.del0 +  1j * params.gamma * params.L * ((1-params.fR) * abs_E + params.fR * RA)
            k0 = params.E + params.E_in_prof * params.E_in_mag/NL
            E_NL = k0* np.exp(NL*params.h) - params.E_in_prof * params.E_in_mag/NL

            E_f = ifft(E_NL)
            E_dispersion  = E_f * np.exp(params.dispersion*params.h)
            params.E = fft(E_dispersion)

        # print('\r' + str(params.rt_counter), end = '')

    def params_constructor(self):
        params = self.params_c
        f_sample = params.f_sample

        params.E_in_mag = np.sqrt(params.P_in * params.theta1)

        # """Raman response calculated with correct grid then shifted"""
        params.RR_f = fftshift(rc.Raman_res_interp(fftshift(f_sample/2/np.pi)))
        params.h = 1/params._N

        betak = params.betak
        dispersion = 0 
        for n in betak.keys():
            if n <= params.order:
                dispersion += f_sample**n / factorial(n) * betak[n]
        dispersion = 1j*params.L * (dispersion - f_sample * params.d)
        params.dispersion = dispersion

    # def __repr__(self):
    #     return "LLE_SSF default"

NumInt_LLE_ssf_class.__name__ = 'LLE_SSF defualt'
