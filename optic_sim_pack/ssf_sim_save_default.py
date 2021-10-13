import pickle as pickle 

from os import mkdir, chdir
from os.path import getsize, isdir
from secrets import token_hex

def save_start(class_obj):
    class_obj.file_counter = 0 
    class_obj.file_token = token_hex(3)
    class_obj.file_name = class_obj.file_token + '_ssf_save_' 
    
    if isdir('./ssf_save'):
        chdir('./ssf_save')
    else:
        mkdir('./ssf_save')
        chdir('./ssf_save')

    init_file = {'params': class_obj.params,
                 'E_in': class_obj.E_in,
                 'E_init': class_obj.E_init,
                 'token': class_obj.file_token}

    with open(class_obj.file_token + '_init', 'wb') as handle:
        pickle.dump(init_file, handle)

    with open(class_obj.file_name + str(class_obj.file_counter), 'wb') as handle:
        pass

def save_update(class_obj):
    out_array = [class_obj.rt_counter, class_obj.params_list[1], class_obj.E]
    if getsize(class_obj.file_name + str(class_obj.file_counter))/1024**2 > 500:
        class_obj.file_counter += 1
    else:
        pass 

    with open(class_obj.file_name + str(class_obj.file_counter), 'ab') as handle:
        pickle.dump(out_array, handle)
    

