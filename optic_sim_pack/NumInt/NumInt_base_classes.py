import numpy as np 

from numpy.fft import fftshift
from warnings import warn

c = 3e8
class _plot_control_base():
    def __init__(self, params_c, status_c): warn('base plot class __init__() called', RuntimeWarning, stacklevel= 2) 
    def plot_update(self): pass 
    def plot_start(self): pass 
    def plot_final(self): pass 

class _save_control_base():
    def __init__(self, params_c, status_c): warn('base save class __init__() called', RuntimeWarning, stacklevel= 2) 
    def save_update(self): pass 
    def save_start(self): pass 
    def save_final(self): pass 

class _integration_manager_base():
    """base class of integration manager, contain skeleton structure and default functions"""
    def __init__(self):
        self.grid_constructor()
        self.params_constructor()
        self.params_c.rt_counter = None
        self.status_c.integration_mode = self.__repr__()

        self.plot_control = self.plot_control_class(self.params_c, self.status_c)
        self.save_control = self.save_control_class(self.params_c, self.status_c)

        self.int_manager_init_call()
        
        self.status_c.base_initialised = True

    def grid_constructor(self):
        """Default temporal/spectral/wavelength grid constructor"""
        params = self.params_c

        npt = params.npt
        t_span = params.tspan
        
        grid = np.linspace(-npt/2, npt/2, npt, endpoint = False)/npt 
        params.t_sample = grid * t_span
        params.f_plot = f_plot = grid * npt/t_span
        # """reverse freq_grid for integrator step"""
        params.f_sample = fftshift(f_plot* 2 *np.pi)

        if 'wl_pump' in params:
            # """check minimum temporal duration"""
            t_span_lim = params.npt/(c/params.wl_pump * 2) 
            if params.tspan <= t_span_lim:
                raise ValueError('tspan beyond limit, min tspan = {}'.format(t_span_lim)) 
            
            lam_grid = c/(f_plot + c/params.wl_pump) * 1e9
        else:
            lam_grid = None 

        params.lam_grid = lam_grid

    def params_constructor(self): 
        warn('no params constructor found', RuntimeWarning, stacklevel= 2)

    def integration_step(self):
        raise NotImplementedError('Integration step not implemented; Sim terminated')

    def int_manager_init_call(self): print('int init default')

    def plotting_processing(self): pass 

    def saving_processing(self): pass 

    def common_processing(self): pass 

    def termination_processing(self): pass 

    def integrate(self): 
        params = self.params_c
        status = self.status_c
        plot_control = self.plot_control
        save_control = self.save_control
        trig = min(params._S_intv, params._P_intv)

        if status.saving:
            if not status.save_started:
                save_control.save_start()
        else: pass

        if status.plotting:
            if not status.plot_started:
                plot_control.plot_start()
        else: pass         

        try:
            for params.rt_counter in range(1, int(params._M) + 1):

                self.integration_step()

                if not params.rt_counter%trig or status.force_proc:
                    
                    if status.plotting and not params.rt_counter%params._P_intv:
                        self.plotting_processing()
                        plot_control.plot_update()


                    if status.saving and not params.rt_counter%params._S_intv:
                        self.saving_processing()
                        save_control.save_update()

                
                    self.common_processing()

        except (KeyboardInterrupt, StopIteration):
            pass 
        
        if status.plotting:
            self.plot_control.plot_final()
        if status.saving:
            self.save_control.save_final()
        self.termination_processing()
        
        