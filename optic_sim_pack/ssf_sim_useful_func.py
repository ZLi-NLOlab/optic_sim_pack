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
    max_index = len(array)
    lower = c_index
    upper = c_index 
    l_cont = True 
    u_cont = True 
    while True:
        if l_cont:
            if not find_nearst_condi(array[lower - 1], array[lower], val):    
                lower -= 1
            elif lower <= 0:
                lower = 0
                l_cont = False   
            else:
                lower -=1
                l_cont = False  
        
        if u_cont:
            if not find_nearst_condi(array[upper], array[upper + 1], val):
                upper += 1
            elif upper >= max_index:
                lower = max_index
                u_cont = False  
            else:
                upper += 1
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
                data_array.append(data_temp[-1])
        except EOFError:
            pass
    
    return np.asarray(data_array)

