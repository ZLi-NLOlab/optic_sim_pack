import numpy as np 

from numpy.fft import fft, ifft, fftshift
from functools import partial

class NumInt_LLE_class():

    def integration_step(self, E, E_in_prof, E_in_mag, del0, alpha, L, gamma, fr, RR_f, dispersion, h, N):
        """integrator for LLE using ssf, performed in fftshifted grid"""
        for temp in range(N):
            abs_E = np.abs(E)**2

            RA = RR_f * ifft(abs_E)
            RA = fft(RA)

            NL = -alpha - 1j*del0 +  1j * gamma * L * ((1-fr) * abs_E + fr * RA)
            k0 = E + E_in_prof * E_in_mag/NL
            E_NL = k0* np.exp(NL*h) - E_in_prof * E_in_mag/NL

            E_f = ifft(E_NL)
            E_dispersion  = E_f * np.exp(dispersion*h)
            E = fft(E_dispersion)

        return E

    def params_constructor(self, params):
        params = self.params
        f_sample = self.f_sample
        # """Raman response calculated with correct grid then shifted"""
        RR_f = fftshift(self.Raman_res_interp(fftshift(f_sample/2/np.pi)))
        h = 1/params['M_N'][1]

        betak = params['betak']
        dispersion = 0 
        for n in betak.keys():
            if n <= params['order']:
                dispersion += f_sample**n / factorial(n) * betak[n]
        dispersion = 1j*params['L'] * (dispersion - f_sample * params['d'])

        out_list = [np.sqrt(params['P_in'] * params['theta1']),
                    params['alpha'],
                    params['del0'],
                    params['gamma'],
                    params['L'],
                    params['fR'],
                    RR_f, dispersion, h
                    ]

        return out_list        
