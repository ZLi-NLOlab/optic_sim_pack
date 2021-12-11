import pickle as pickle 

from os import mkdir, chdir
from os.path import isdir, isfile
from secrets import token_hex

class save_class_default():
    def __init__(self, params_c, status_c):
        self.save_vars = self._save_vars_container()
        self.save_vars.token = token_hex(3)
        self.status_c = status_c
        self.params_c = params_c
        params_c.save_token = self.save_vars.token

    def save_start(self):
        status_c = self.status_c

        if status_c.save_dir == '.':
            self.save_vars.folder_dir = 'NumInt_out_{}'.format(self.save_vars.token)
            mkdir(self.save_vars.folder_dir)            
        elif isdir(status_c.save_dir):
            self.save_vars.folder_dir = status_c.save_dir
        elif not isdir(status_c.save_dir) and status_c.make_dir:
            self.save_vars.folder_dir = status_c.save_dir
            mkdir(self.save_vars.folder_dir)
        else: raise FileNotFoundError('no {} found; input valid save directory or enable make_dir'.format(status_c.save_dir))

        chdir(self.save_vars.folder_dir)
        self.stack_save(self.params_c.params_return(self.status_c.params_save_list), self.get_name('init_params'))
        
        self.status_c.save_started = True

    def save_update(self):
        out_data = self.status_c.save_func(self)
        self.stack_save(out_data, self.get_name('sim_out'))

    def get_name(self, name):
        return self.status_c.save_name + '_' + name + '_' + str(self.save_vars.token)  

    def stack_save(self, data, file):
        with open(file, 'ab') as handle:
            pickle.dump(data, handle)

    class _save_vars_container():
        pass  
    

