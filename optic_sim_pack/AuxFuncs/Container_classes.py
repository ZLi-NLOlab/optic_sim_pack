from warnings import warn

__all__ = ['params_container', 'status_container']

class _container_base():
    def __init__(self, *args, **kargs):
        self.set_params(*args, **kargs)

    def __getitem__(self, key) -> dict:
        if type(key).__name__ == 'str':
            return {key: vars(self)[key]}

        elif type(key).__name__ == 'list' or type(key).__name__ == 'tuple':
            out_dict = dict()
            return dict([(_key_temp, vars(self)[_key_temp]) for _key_temp in key])   
        
        else: raise TypeError

    def __call__(self, key):
        if type(key).__name__ != 'str': raise TypeError
        else:
            return vars(self)[key]

    def __iter__(self):
        return iter(vars(self))

    def set_params(self, *args, **kargs):
        for args_temp in args:
            if type(args_temp) != dict:
                raise TypeError('non-keyword argument of params container must be dict')
            for keys_temp in args_temp:
                keys_temp_ori = keys_temp
                if ' ' in keys_temp:
                    keys_temp = keys_temp.replace(' ', '_')
                self.__setattr__(keys_temp, args_temp[keys_temp_ori]) 
        
        for keys_temp in kargs:
            self.__setattr__(keys_temp, kargs[keys_temp]) 

    def remove(self, *args):
        for arg_temp in args:
            if type(arg_temp) != str:
                warn('incorrect entry type, only str taken, skipped', RuntimeWarning, stacklevel= 2)
                continue 

            if arg_temp not in vars(self):
                warn('no "{}" found, skipped'.format(arg_temp), RuntimeWarning, stacklevel= 2)
                continue

            delattr(self, arg_temp)

class params_container(_container_base):

    def get_params_list(self, params_list) -> list:
        if type(params_list).__name__ == 'list':
            return [vars(self)[_key_temp] for _key_temp in params_list]
        elif type(params_list).__name__ == 'str':
            return [vars(self)[params_list]]
        else: raise TypeError

    def __repr__(self):
        return "params_container:\n{} \n{}".format(list(vars(self).keys()), str(vars(self)))

class status_container(_container_base):
    def __init__(self, *args, text_list = None, **kargs ):
        super().__init__(*args, **kargs)
        if text_list == None:
            self.text_list = list(vars(self).keys())
        else:
            self.text_list = text_list
    
    def print_status(self, status_list = None) -> str:
        text = ""
        if status_list == None:
            for n in self.text_list:
                text += "{} = {},\n".format(str(n), vars(self)[n])
        else:
            for n in status_list:
                if n not in vars(self):
                    continue
                text += "{} = {},\n".format(str(n), vars(self)[n])            
        return text

    def __repr__(self):
        return "status_container:\n{} \n{}".format(list(vars(self).keys()), str(vars(self)))