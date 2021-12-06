import numpy as np 

from functools import partialmethod, partial
from numpy.fft import fftshift, ifft, fft 
from . import ssf_sim_aux as aux
from . import ssf_sim_raman_aux as ra

c = 3e8

class ssf_sim_class():
    def __init__(self, params, E_init = None, E_in_prof = None, 
                    plotting = False, saving = False, force_proc = False,
                    *args, **kargs):

    #    """-----------------------------------------------------------"""
    #    """Class variables initialisation"""

        self.plotting = plotting 
        self.saving = saving
        self.force_proc = force_proc
 
        self.params = params
        self.params_list = None
        self.fig_started = False
        self.save_started = False
        self.integration_mode = None

        self.grid_constructor()
        
        #"""Initial E field, if E_init not provided, random initial field is used"""
        if E_init is None:
            self.E_init = (np.random.rand(params['npt']) + 1j * np.random.rand(params['npt'])) * 1e-12
        elif type(E_init).__name__ == "function":
            self.E_init = E_init(self.t_sample) 
        elif type(E_init).__name__ in ["list", "ndarray"]:
            self.E_init = E_init
        else:
            raise TypeError('Invalid E_init type')

        # """Note that E_in_prof is the input field profile with amplitude normalized to 1, 
        # function can be used as an input with t_sample as variable,
        # if no provided CW field is used"""
        if E_in_prof is None:
            self.E_in_prof = np.ones(self.params['npt'])
        elif type(E_in_prof).__name__ == "function":
            self.E_in_prof = E_in_prof(self.t_sample) 
        elif type(E_in_prof).__name__ in ["list", "ndarray"]:
            self.E_in_prof = E_in_prof
        else:
            raise TypeError('Invalid E_in_prof type')
        
        
        if 'fig_mod' in kargs:
            self.fig_initiate(fig_mod = kargs['fig_mod'])

        else:
            from . import ssf_sim_fig_default as fig_default
            self.fig_initiate(fig_mod = fig_default)

        if 'save_mod' in kargs:
            self.save_initiate(save_mod = kargs['save_mod'])
        else:
            from . import ssf_sim_save_default as save_default
            self.save_initiate(save_mod = save_default)
    
        if 'Raman_mode' in kargs:
            if kargs['Raman_mode'] == 'Sing Osc':
                if 'RR_tau' in self.params:
                    self.Raman_res_interp = lambda f_plot: ra.Raman_res_interp(f_plot, Raman_mod= ra.Raman_res_SigDamped(*self.params['RR_tau']))
                else:
                    self.Raman_res_interp = lambda f_plot: ra.Raman_res_interp(f_plot, Raman_mod= ra.Raman_res_SigDamped())
                
        else:
            self.Raman_res_interp = lambda f_plot: ra.Raman_res_interp(f_plot, Raman_mod= ra.Raman_res_multiV())

    """imported method"""
    grid_constructor = partialmethod(aux.grid_constructor)
    params_list_constructor = partialmethod(aux.params_list_constructor)
    integration_step = partialmethod(aux.integration_step)

    def fig_initiate(self, fig_mod):
        """figure initiator, the figure module can be custom designed with two component
        the fig_constructor which construct the figure and assign all necessary values, and 
        the fig_update which is called every rt%p_interval == 0"""

        self.fig_constructor = partial(fig_mod.fig_constructor, self)
        self.fig_update = partial(fig_mod.fig_update, self)
        
    
    def save_initiate(self, save_mod):
        """save inititator, saving module can be custom defined with two component, save start which is called 
        right before integrator is called, and the save_update which is called every rt%s_interval == 0"""

        self.save_start = partial(save_mod.save_start, self)
        self.save_update = partial(save_mod.save_update, self)

    def rt_processing(self):
        """rt_processing can be custom defined, called every roundtrip"""
        pass 
    
    def plotting_processing(self):
        """same as rt_processing, but called every plotting call"""
        pass 

    def saving_processing(self):
        """same as rt_processing, but called every saving call"""
        pass 

    def common_processing(self):
        """called smallest of plotting or saving call, regardless of save/plot state""" 
        pass

    def integ_param_const(self):
        self.params_list = self.params_list_constructor()

    def integration(self):
        E = self.E_init
        
        M, N = self.params['M_N']
        s_interval, p_interval = self.params['S_P']

        # """param list in the following order:
        # 0 P_in, 1 alpha, 2 del0, 3 gamma, 4 L, 5 fR, 6 RR_f, 7 dispersion, 8 h"""
        
        if self.params_list == None:
            self.params_list = self.params_list_constructor()
        else: pass 

        processing_state = any([self.plotting, self.saving, self.force_proc])
        self.rt_counter = 0

        if self.saving:
            if not self.save_started:
                self.save_start()
        else: pass

        if self.plotting:
            if not self.fig_started:
                self.fig_constructor()
        else: pass 
        
        while True:

            E = self.integration_step(E, self.E_in_prof, *self.params_list, N)

            self.rt_counter += 1

            self.E = E
            self.rt_processing()

            if processing_state:
                
                if self.plotting:
                    if self.rt_counter%p_interval == 0:
                        self.plotting_processing()
                        self.fig_update()

                if self.saving:
                    if self.rt_counter%s_interval == 0:
                        self.saving_processing()
                        self.save_update()

                self.common_processing()