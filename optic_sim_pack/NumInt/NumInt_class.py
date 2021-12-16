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
            integration_method = 'LLE_ssf',
            plot_control_class = plot_class_default, 
            save_control_class = save_class_default,
            save_name = 'NumInt', tar_final = False, tar_remove = False,
            **kargs):

    #    """-----------------------------------------------------------"""
    #    """Class variables initialisation"""

        # """integration method selection"""
        if type(integration_method).__name__ == 'str':
            if integration_method == 'LLE_ssf':
                integration_method = NumInt_method.NumInt_LLE_ssf_class
            elif integration_method == 'LLE_ikeda':
                integration_method = NumInt_method.NumInt_LLE_ikeda_class
            elif integration_method == 'NLSE_ssf':
                integration_method = NumInt_method.NumInt_NLSE_ssf_class
            else: raise NotImplementedError('integration method not found; {}'.format(NumInt_method.__doc__))
        elif type(integration_method).__name__ == 'type':
            pass 
        else: raise TypeError('invalid integration method input')

        # """ensuring inputed integration_method does not have __init__()"""
        if '__init__' in integration_method.__dict__:
            raise TypeError('integration method must not contain __init__(), initialisation call can be delegated to int_init_call()')

        # """creating status and params containter"""
        self.params_c = params_container(params)
        self.status_c  = status_container(
            {   'plotting' : plotting,
                'saving': saving,
                'force_proc': force_proc,
                'base_initialised': False,
                'save_name': save_name,
                'save_dir': Path(kargs['save_dir']) if 'save_dir' in kargs else Path.cwd(), 
                'NumInt_method': integration_method.__name__, 
                **({'params_save_list': integration_method.__dict__['default_params_save_list']} if 'default_params_save_list' in integration_method.__dict__ else {}),
                **({'data_save_list': integration_method.__dict__['default_data_save_list']} if 'default_data_save_list' in integration_method.__dict__ else {}),
                **(kargs['status_c_attri'] if 'status_c_attri' in kargs else {})
            })

        # """dynamically create integration_manager class"""
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
        
        # """Initial E field, if E_init not provided, random initial field is used"""
        if E_init is None:
            self.params_c.E = (np.random.rand(self.params_c.npt) + 1j * np.random.rand(self.params_c.npt)) * 1e-12
        elif type(E_init).__name__ == "function":
            self.params_c.E = E_init(self.params_c) 
        elif type(E_init).__name__ == "list":
            self.params_c.E = np.asarray(E_init)
        elif type(E_init).__name__ == "ndarray":
            self.params_c.E = E_init
        else:
            raise TypeError('Invalid E_init type')

        # """Initial E_in profile, if E_in_prof not provided, CW driving is assumed"""
        if E_in_prof is None:
            self.params_c.E_in_prof = np.ones(self.params_c.npt)
        elif type(E_in_prof).__name__ == "function":
            self.params_c.E_in_prof = E_in_prof(self.params_c) 
        elif type(E_in_prof).__name__ == "list":
            self.params_c.E_in_prof = np.asarray(E_init)
        elif type(E_in_prof).__name__ == "ndarray":
            self.params_c.E_in_prof = E_init
        else:
            raise TypeError('Invalid E_init type')    

        del params

    def launch(self):
        if not self.status_c.base_initialised:
            raise RuntimeError('integration manager failed to initialise')

        self.integration_manager.integrate()