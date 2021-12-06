raise ImportError('Unimplemented yet')

from abc import * 

class NumInt_step_base(ABC):
    
    @abstractmethod
    def params_constructor(self):
        pass 

    @abstractmethod 
    def ingetrate_step(self):
        pass 

class fig_base(ABC):
    pass 