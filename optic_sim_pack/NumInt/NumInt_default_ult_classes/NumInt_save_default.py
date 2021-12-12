import pickle as pickle 
import tarfile as tarfile

from os import mkdir, chdir, unlink, rmdir, walk
from os.path import isdir, basename
from pathlib import Path 
from secrets import token_hex
from warnings import warn

class save_class_default():
    def __init__(self, params_c, status_c):
        self.save_vars = self._save_vars_container()
        self.save_vars.token = token_hex(3)
        self.save_vars.cwd = Path.cwd()

        self.status_c = status_c
        self.params_c = params_c
        # params_c.save_token = self.save_vars.token

    def save_start(self):
        status_c = self.status_c

        self.save_vars.folder_dir = Path.joinpath(status_c.save_dir, self.get_name('folder'))
        self.save_vars.folder_dir.mkdir()
        chdir(self.save_vars.folder_dir)

        self.stack_save(self.params_c.params_return(self.status_c.params_save_list), self.get_name('init_params', fold_name= False))
        
        self.status_c.save_started = True

    def save_update(self):
        out_data = self.status_c.save_func(self)
        self.stack_save(out_data, self.get_name('data', fold_name= False))

    def get_name(self, name = None, fold_name = True):
        if fold_name:
            inter_text = '_'
        else: inter_text = '.'
        if name == None: 
            text = '{}{}{}'.format(self.status_c.save_name, inter_text, str(self.save_vars.token))
        else: 
            text = '{}_{}{}{}'.format(self.status_c.save_name, name, inter_text, str(self.save_vars.token), )
    
        return text

    def stack_save(self, data, file):
        with open(file, 'ab') as handle:
            pickle.dump(data, handle)

    def save_final(self):
        if self.status_c.tar_final and str(self.save_vars.token) in self.save_vars.folder_dir.name:
            chdir(self.save_vars.folder_dir.parent)
            with tarfile.open(self.get_name('sim_out.gz.tar', fold_name= False), 'w:gz') as handle:
                handle.add(self.save_vars.folder_dir.name)
            if self.status_c.tar_remove:
                self._clear_folder()

        else: pass 
        chdir(self.save_vars.cwd)

    def _clear_folder(self):
        fold_dir = self.save_vars.folder_dir
        if not fold_dir.is_dir():
            warn('save dir path does not exist; clear folder skipped', UserWarning, stacklevel= 2)
        elif str(self.save_vars.token) not in fold_dir.name:
            warn('incorrect save dir path stored; clear folder skipped', UserWarning, stacklevel= 2) 
        else:
            fold_list = [n for n in walk(fold_dir, topdown= False)]
            for fold_N in fold_list:
                for file_N in fold_N[2]:
                    unlink(Path.joinpath(Path(fold_N[0]), Path(file_N)))
                rmdir(fold_N[0])

    class _save_vars_container():
        pass  
    

