import numpy as np 
import pickle as pickle

from numpy.fft import fftshift
from warnings import warn

c = 3e8

class _plot_control_base():
    def __init__(self, params_c, status_c): warn('base plot class __init__() called', RuntimeWarning, stacklevel= 2) 
    def plot_update(self): pass 
    def plot_start(self): pass 
    def plot_final(self): print('save_final') 

class _save_control_base():
    def __init__(self, params_c, status_c): warn('base save class __init__() called', RuntimeWarning, stacklevel= 2) 
    def save_update(self): pass 
    def save_start(self): pass 
    def save_final(self): print('plot_final') 


class _container_base():
    def __init__(self, *args, **kargs):
        self.set_params(*args, **kargs)

    def set_params(self, *args, **kargs):
        for args_temp in args:
            if type(args_temp) != dict:
                raise TypeError('non-keyword argument of params container must be dict')
            for keys_temp in args_temp:
                keys_temp_ori = keys_temp
                if ' ' in keys_temp:
                    keys_temp = keys_temp.replace(' ', '_')
                self.__setattr__(keys_temp, args_temp[keys_temp_ori]) 
        
        for keys_temp in kargs:
            self.__setattr__(keys_temp, kargs[keys_temp]) 

    def remove(self, *args):
        for arg_temp in args:
            if type(arg_temp) != str:
                warn('incorrect entry type, only str taken, skipped', RuntimeWarning, stacklevel= 2)
                continue 

            if arg_temp not in vars(self):
                warn('no "{}" found, skipped'.format(arg_temp), RuntimeWarning, stacklevel= 2)
                continue

            delattr(self, arg_temp)

    def __iter__(self):
        return iter(vars(self))

class params_container(_container_base):

    # def __getitem__(self, key):
    #     return vars(self)[key]
    def params_return(self, params_list):
        if params_list == None: 
            params_list = vars(self).keys()
        else: pass 

        return dict([(_key_temp, vars(self)[_key_temp]) for _key_temp in params_list])         

    def __repr__(self):
        return "params_container:\n{} \n{}".format(list(vars(self).keys()), str(vars(self)))

class status_container(_container_base):
    def __init__(self, *args, text_list = None, **kargs ):
        super().__init__(*args, **kargs)
        if text_list == None:
            self.text_list = list(vars(self).keys())
        else:
            self.text_list = text_list
    
    def print_status(self, status_list = None):
        text = ""
        if status_list == None:
            for n in self.text_list:
                text += "{} = {},\n".format(str(n), vars(self)[n])
        else:
            for n in status_list:
                if n not in vars(self):
                    continue
                text += "{} = {},\n".format(str(n), vars(self)[n])            
        return text

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
        
        self.status_c.initialised = True

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

    def int_manager_init_call(self): pass 

    def plotting_processing(self): pass 

    def saving_processing(self): pass 

    def common_processing(self): pass 

    def termination_processing(self): pass 

    def integrate(self): 

        params = self.params_c
        status = self.status_c
        plot_control = self.plot_control
        save_control = self.save_control
        trig = min(params._S, params._P)

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
                    
                    if status.plotting and params.rt_counter%params._S:
                        self.plotting_processing()
                        plot_control.plot_update()

                    if status.saving and params.rt_counter%params._P:
                        self.saving_processing()
                        save_control.save_update()
                
                    self.common_processing()

        except (KeyboardInterrupt, StopIteration):
            pass 
        
        if status.saving:
            self.save_control.save_final()
        if status.plotting:
            self.plot_control.plot_final()
        self.termination_processing()
        
        