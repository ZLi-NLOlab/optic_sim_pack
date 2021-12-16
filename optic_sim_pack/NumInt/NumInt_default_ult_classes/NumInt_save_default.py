import tarfile as tarfile

from os import chdir, unlink, rmdir, walk
from pathlib import Path 
from secrets import token_hex
from warnings import warn

from ...AuxFuncs.AuxFunc_load_save import stack_save

class save_class_default():

    def __init__(self, params_c, status_c):
        self.save_vars = self._save_vars_container()
        self.save_vars.token = token_hex(3)
        self.save_vars.cwd = Path.cwd()

        self.status_c = status_c
        self.params_c = params_c

        self._status_check()
    
    def save_start(self):
        status_c = self.status_c

        self.save_vars.folder_dir = Path.joinpath(status_c.save_dir, self.get_name('folder'))
        self.save_vars.folder_dir.mkdir()
        chdir(self.save_vars.folder_dir)

        stack_save({**self.params_c[self.status_c.params_save_list], **status_c['data_save_list']}, 
                self.get_name(extension = '.params', fold_name= False, token_extension= False))
        self.status_c.save_started = True

    def save_update(self):
        out_data = self.params_c.get_params_list(self.status_c.data_save_list)
        stack_save(out_data, self.get_name(extension = '.data', fold_name= False, token_extension= False))

    def save_final(self):
        if self.status_c.tar_final and str(self.save_vars.token) in self.save_vars.folder_dir.name:
            print('tarring output')
            chdir(self.save_vars.folder_dir.parent)
            with tarfile.open(self.get_name(extension = '.simout.tar.gz', fold_name= False), 'w:gz') as handle:
                handle.add(self.save_vars.folder_dir.name)
            if self.status_c.tar_remove:
                self._clear_folder()

        else: pass 
        chdir(self.save_vars.cwd)

    def get_name(self, name = None, extension = None, fold_name = True, token_extension = True):
        if name == None:
            text = self.status_c.save_name
        else: 
            text = self.status_c.save_name + '_' + str(name)
        
        if extension != None:
            text += extension
        else: pass 

        if token_extension:
            if fold_name:
                text += '_{}'.format(self.save_vars.token)
            else:
                text += '.{}'.format(self.save_vars.token)
        return text



    def _status_check(self):
        status_c = self.status_c

        status_c.save_started = False
        if 'data_save_func' not in status_c:
            status_c.data_save_func = lambda cls: [cls.params_c.rt_counter, cls.params_c.E]
        else: pass

        if 'params_save_list' not in status_c:
            status_c.params_save_list = list(vars(self.params_c).keys())
        else: pass 

        if 'data_save_list' not in status_c:
            status_c.data_save_list = ['rt_counter', 'E']

        if 'tar_final' not in status_c:
            status_c.tar_final = False
        else: pass 

        if 'tar_remove' not in status_c:
            status_c.tar_remove = False 
        else: pass 
        
    def _clear_folder(self):
        fold_dir = self.save_vars.folder_dir
        if not self.status_c.save_started:
            warn('save not started; clear folder skipped', UserWarning, stacklevel= 2)
        elif not fold_dir.is_dir():
            warn('save dir path does not exist; clear folder skipped', UserWarning, stacklevel= 2)
        elif str(self.save_vars.token) not in fold_dir.name:
            warn('incorrect save dir path stored; clear folder skipped', UserWarning, stacklevel= 2) 
        elif self.status_c.save_started and fold_dir.is_dir() and (str(self.save_vars.token) in fold_dir.name):
            fold_list = [n for n in walk(fold_dir, topdown= False)]
            for fold_N in fold_list:
                for file_N in fold_N[2]:
                    unlink(Path.joinpath(Path(fold_N[0]), Path(file_N)))
                rmdir(fold_N[0])
        else:
            warn('unknown error occurred during folder clearing; clear folder skipped', UserWarning, stacklevel= 2)

    class _save_vars_container():
        pass  
    

