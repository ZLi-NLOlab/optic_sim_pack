import pickle as pickle 
import tarfile as tarfile

def get_extension(name) -> str:
    return(name.split('.')[-1])

def unique_name(name, ref) -> str:
    counter = 1
    if name in ref:
        while name + '_' + str(counter) in ref:
            counter += 1
        return name + '_' + str(counter)
    else: return name

def stack_save(data, name):
    with open(name, 'ab') as handle:
        pickle.dump(data, handle)

def stack_load(name) -> list:
    out_temp = []
    with open(name, 'rb') as handle:
        try: 
            while True:
                out_temp.append(pickle.load(handle))
        except EOFError: pass
    return out_temp

def tar_load_NumInt(name) -> dict:
    with tarfile.open(name, 'r:gz') as handle:
        out_dict = dict()
        for tar_obj in handle:
            name = tar_obj.name; extension = get_extension(tar_obj.name)
            
            if not tar_obj.isfile():
                continue
            
            if extension == 'data':
                _out_list_temp = [] 
                with handle.extractfile(tar_obj) as pickle_handle:
                    try:
                        while True:
                            _out_list_temp.append(pickle.load(pickle_handle))
                    except EOFError: pass 
                out_dict[extension] = _out_list_temp
            else:
                out_dict[extension] = pickle.load(handle.extractfile(tar_obj))

    return out_dict



        
