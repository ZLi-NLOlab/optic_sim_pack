import numpy as np 
import pickle as pickle 

def find_nearst_condi(a,b,c):
    if a < c <= b or b <= c < a:
        return True 
    else: return False 

def find_nearst(val, array):
    for n in range(len(array)-1):
        if find_nearst_condi(array[n], array[n+1], val):
            return [n, n+1]

def FWHM_find(val, array):
    c_index = np.where(array == np.nanmax(array))[0][0]
    max_index = len(array) - 1
    lower = c_index
    upper = c_index 
    l_cont = True if c_index != 0 else False
    u_cont = True if c_index != max_index else False

    while True:
        if upper >= (max_index):
            upper = max_index
            u_cont = False 

        if lower <= 0:
            lower = 0
            l_cont = False   

        if l_cont:
            if not find_nearst_condi(array[lower - 1], array[lower], val):    
                lower -= 1
            else:
                lower -=1
                l_cont = False  
        
        if u_cont:
            if not find_nearst_condi(array[upper], array[upper + 1], val):
                upper += 1
            else:
                u_cont = False

        if not any((l_cont, u_cont)):
            break 

    return [lower, upper]
                
def stack_load(name):
    data_array = []
    with open(name, 'rb') as handle:
        try:
            while True:
                data_temp = pickle.load(handle)
                data_array.append(data_temp)
        except EOFError:
            pass
    
    return data_array

