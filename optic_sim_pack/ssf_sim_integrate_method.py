import numpy as np 

from functools import partial
from numpy.fft import ifft, fft 

def integration_step_LLE_ssf(self, E, E_in_prof, alpha, del0, E_in_mag, gamma, L, fr, RR_f, dispersion, h, N):
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

def LLE_ssf(class_obj):
    """Selector func for base_class, Lugiato-Lefever with split-step Fourier"""
    class_obj.integration_mode = 'LLE split-step Fourier'
    class_obj.integration_step = partial(integration_step_LLE_ssf, class_obj)

def integration_step_NLSE_ssf(class_obj, E, E_in, alpha, del0, gamma, L, fr, RR_f, dispersion, h, N):
    abs_E = np.abs(E)**2

def NLSE_ssf(class_obj):
    """Selector func for base_class"""
    class_obj.integration_mode = 'NLSE split-step Fourier'
    class_obj.integration_step = partial(integration_step_NLSE_ssf, class_obj)
