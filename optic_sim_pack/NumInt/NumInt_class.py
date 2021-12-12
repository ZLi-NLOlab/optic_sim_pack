import numpy as np 

from functools import partialmethod, partial
from numpy.fft import fftshift, ifft, fft 
from pathlib import Path

from . import NumInt_method  
from ..AuxFuncs import params_container, status_container
from .NumInt_base_classes import  _integration_manager_base, _save_control_base, _plot_control_base
from .NumInt_default_ult_classes import plot_class_default, save_class_default


class NumInt_class():
    """
    Numerical integration class

    Parameters
    ----------
    -- params : dict | required
        A dictionary contain all varaible required for simulations. 
    -- E_init : list, ndarray or function(t_sample) | optional
        Initial E field, random field is used if no input is provided.
    -- E_in_prof : list, ndarray or function(t_sample) | optional 
        Driving field profile, CW driving is assumed if no input is provided.
    -- plotting : bool | optional 
        Turn plotting on/off, default off. 
    -- saving : bool | optional
        Turn saving on/off, default off.   
    -- plot_control_class : class | optional
        control class that define plotting behaviour, 
        namely the save_start() which defines initalisation behaviour 
        and save_update() which is called every plotting interval. 
        If none is provided, the defualt figure class is used.
    -- save_control_class : class | optional 
        control class that define saving behaviour, similar to plot_control_class.

    Avaliable **kargs:
    Processing calls : class memeber function 
        --int_manager_init_call : called at the end of integration_manager __init__().
        --plotting_processing : called before plot_update().
        --saving_processing : called before save_update().    
        --common_processing : called at the end of each processing block.
        --termination_processing : called as integration() is completed.

        These function calls should be defined as class memeber functions, if no 
        input provided then simple pass function is used. The call order is as 
        listed.
    
    Explaination
    ----------    
    This is the initialisation class for the Numerical simulation. 

    Note
    ----------    
    - The integration() call of the integration_mananger is designed to catch 
    KeyboardInterrupt and StopIteration exceptions. So if one intended to raise 
    exception call within integration() call, do not raise the above two.   

    """
    def __init__(self,  
            params, 
            E_init = None, 
            E_in_prof = None, 
            plotting = False, saving = False, force_proc = False,
            # NumInt_method = 'LLE_ssf',
            plot_control_class = plot_class_default, 
            save_control_class = save_class_default,
            save_name = 'NumInt', tar_final = False, tar_remove = False,
            **kargs):

    #    """-----------------------------------------------------------"""
    #    """Class variables initialisation"""

        integration_method = NumInt_method.NumInt_LLE_ssf_class

        self.params_c = params_container(params)
        self.status_c  = status_container(
            {   'plotting' : plotting,
                'saving': saving,
                'force_proc': force_proc,
                'plot_started': False,
                'save_started': False, 
                'save_name': save_name,
                # 'save_dir': kargs['save_dir'] if 'save_dir' in kargs else '.',
                'save_dir': Path(kargs['save_dir']) if 'save_dir' in kargs else Path.cwd(), 
                'tar_final': tar_final, 
                'tar_remove': tar_remove,
                'params_save_list': kargs['params_save_list'] if 'params_save_list' in kargs else None, 
                'status_plot_list': kargs['status_plot_list'] if 'status_plot_list' in kargs else ['saving', 'plotting', 'save_started', 'plot_started', 'force_proc', 'NumInt_method'],
                'save_func': kargs['save_func'] if 'save_func' in kargs else lambda cls: [cls.params_c.rt_counter, cls.params_c.E], 
                'NumInt_method': integration_method.__name__,
                # 'root_dir': getcwd()
            })

        self._integration_manager_class = type(
            'integration_manager', 
            (   integration_method,
                _integration_manager_base,
            ),
            {   'params_c': self.params_c,
                'status_c': self.status_c,
                'plot_control_class': type('plot_control_class', (plot_control_class, _plot_control_base), {}) if plot_control_class != None else _plot_control_base,
                'save_control_class': type('save_control_class', (save_control_class, _save_control_base), {}) if save_control_class != None else _save_control_base,
                **({'int_manager_init_call': kargs['int_init_call']} if 'int_init_call' in kargs else {}),
                **({'common_processing': kargs['common_proc_call']} if 'common_proc_call' in kargs else {}),
                **({'termination_processing': kargs['termination_proc_call']} if 'termination_proc_call' in kargs else {}),
                **({'plotting_processing': kargs['plot_proc_call']} if 'plot_proc_call' in kargs else {}),
                **({'saving_processing': kargs['save_proc_call']} if 'save_proc_call' in kargs else {}),
                
            }
        )
        self.integration_manager = self._integration_manager_class()
        
        #"""Initial E field, if E_init not provided, random initial field is used"""
        if E_init is None:
            self.params_c.E = (np.random.rand(self.params_c.npt) + 1j * np.random.rand(self.params_c.npt)) * 1e-12
        elif type(E_init).__name__ == "function":
            self.params_c.E = E_init(self.params_c.t_sample) 
        elif type(E_init).__name__ == "list":
            self.params_c.E = np.asarray(E_init)
        elif type(E_init).__name__ == "ndarray":
            self.params_c.E = E_init
        else:
            raise TypeError('Invalid E_init type')

        if E_in_prof is None:
            self.params_c.E_in_prof = np.ones(self.params_c.npt)
        elif type(E_in_prof).__name__ == "function":
            self.params_c.E_in_prof = E_in_prof(self.params_c.t_sample) 
        elif type(E_in_prof).__name__ == "list":
            self.params_c.E_in_prof = np.asarray(E_init)
        elif type(E_in_prof).__name__ == "ndarray":
            self.params_c.E_in_prof = E_init
        else:
            raise TypeError('Invalid E_init type')    

        del params

    def launch(self):
        self.integration_manager.integrate()