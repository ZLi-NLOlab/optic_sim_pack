from warnings import warn

class _container_base():
    def __init__(self, *args, **kargs):
        self.set_params(*args, **kargs)

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

    def __iter__(self):
        return iter(vars(self))

class params_container(_container_base):

    def __getitem__(self, key):
        return vars(self)[key]

    def params_return(self, params_list):
        if params_list == None: 
            params_list = vars(self).keys()
        else: pass 

        return dict([(_key_temp, vars(self)[_key_temp]) for _key_temp in params_list])         

    def __repr__(self):
        return "params_container:\n{} \n{}".format(list(vars(self).keys()), str(vars(self)))

class status_container(_container_base):
    def __init__(self, *args, text_list = None, **kargs ):
        super().__init__(*args, **kargs)
        if text_list == None:
            self.text_list = list(vars(self).keys())
        else:
            self.text_list = text_list
    
    def print_status(self, status_list = None):
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