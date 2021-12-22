import numpy as np 
import pickle as pickle 

from scipy.interpolate import interp1d

def cw_return(del0, alpha, P_in, gamma, L, theta) -> tuple:
    Delta = del0/alpha
    X = P_in * (gamma * L * theta)/alpha**3
    roots = np.roots([1, -2*Delta, 1+Delta**2, -X])
    root = []
    for n_temp in roots:
        if np.imag(n_temp) == 0:
            root.append(n_temp)

    sol_min = (min(root) * 1/(gamma * L/alpha)).real
    sol_max = (max(root) * 1/(gamma * L/alpha)).real

    return sol_min, sol_max
    
def find_nearst_condi(a,b,c) -> bool:
    if a < c <= b or b <= c < a:
        return True 
    else: return False 

def find_nearst(val, array) -> list:
    for n in range(len(array)-1):
        if find_nearst_condi(array[n], array[n+1], val):
            return [n, n+1]

def fwhm_find(val, array) -> tuple:
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
                
def find_zero(array, fine = True) -> np.ndarray:
    zero_cross = []
    for index in range(len(array) -1):
        if np.sign(array[index]) != np.sign(array[index+1]):
            zero_cross.append(index)

    if fine or not len(zero_cross): pass 
    else: 
        for n_temp in range(len(zero_cross)):
            index = zero_cross[n_temp]
            inter_temp = interp1d(array[[index, index + 1]], [index, index + 1])
            zero_cross[inter_temp(0)]

    return np.asarray(zero_cross)
