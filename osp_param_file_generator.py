import numpy as np
from load_save_func import save

c = 3e8

b3_zdw = 1.2949475e-40
b4_zdw = -6.659178e-55
b5_zdw = 0e-71
zdw = 1564.5221e-9
w_zdw = c/zdw * 2 * np.pi
tau1 = 12.2e-15 ; tau2 = 32e-15

def get_dispersion(w_p): 
    
    def b2(w_zdw, w_p, b3, b4, b5):
        b2_ = b3 * (w_p - w_zdw) + b4/2 * (w_p - w_zdw)**2 + b5/6 * (w_p - w_zdw)**3
        return b2_ 
    
    def b3(w_zdw, w_p, b3, b4, b5):
        b3_ = b3 + b4 * (w_p - w_zdw) + b5/2 * (w_p - w_zdw)**2
        return b3_
    
    def b4(w_zdw, w_p, b4, b5):
        b4 = b4 + b5*(w_p - w_zdw)
        return b4
    
    b2_ = b2(w_zdw, w_p, b3_zdw, b4_zdw, b5_zdw)
    b3_ = b3(w_zdw, w_p, b3_zdw, b4_zdw, b5_zdw)
    b4_ = b4(w_zdw, w_p, b4_zdw, b5_zdw)
    disp = {2: b2_, 3: b3_, 4: b4_}
    
    return disp

def param_create():

    params = dict()
    """cavity params"""
    params['finesse'] = 200
    params['alpha'] = np.pi/params['finesse']
    params['gamma'] = 1.8e-3 
    params['L'] = 4
    params['theta1'] =  0.01
    params['fR'] = 0.18 
    params['RR_tau'] = (tau1, tau2)
    
    """driving params"""
    params['P_in'] = 30
    params['d'] =  -124e-15 
    params['del0'] = 1.91 * params['alpha'] 
    params['order'] = 4
    lam_c = params['wl_pump'] = 1500e-9
    params['betak'] = get_dispersion( c/lam_c * 2 * np.pi)
    params['p_in_dur'] = 2e-12 
    # params['RR'] = (12.2e-15, 32e-15 * 2)
 
    """sim params"""
    params['npt'] = 2**14
    params['tspan'] = 100e-12
    params['M_N'] = (20e3, 20)   # max roundtrip, step per roundtrip 
    params['S_P'] = (1, 10)  # save interval, plot interval 

    return params 

def params_save(params):
    save(params, 'raman_sim_params', extension = '.params', overwrite= True)
    print('param created')

if __name__ == '__main__':
    params = param_create()
    params_save(params)
    import raman_ssf_base 

else:
    params = param_create()
    params_save(params)