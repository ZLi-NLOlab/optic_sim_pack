import numpy as np 

from ...AuxFuncs import Raman_calc as rc
from numpy.fft import fft, ifft, fftshift
from math import factorial 

class numint_LLE_ssf_class():

    default_params_save_list = [
        'finesse', 'gamma', 'L', 'theta1', 'fR', 'RR_tau', 'RR_method',
        'P_in', 'd', 'del0', 'order', 'betak',
        'npt', 'tspan', '_M', '_N', '_S_intv', '_P_intv']

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

        params.h = 1/params._N

        betak = params.betak
        dispersion = 0 
        for n in betak.keys():
            if n <= params.order:
                dispersion += f_sample**n / factorial(n) * betak[n]
        dispersion = 1j*params.L * (dispersion - f_sample * params.d)
        params.dispersion = dispersion

numint_LLE_ssf_class.__name__ = 'LLE_SSF defualt'
