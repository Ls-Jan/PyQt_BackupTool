from enum import Enum



class E(Enum):
    a=0

class X:
    def __init__(self,e:E):
        self.e=e
    
X(0)
    