import pyffi
import numpy as np

lib = pyffi.Lib("./global_functions.so")

class Mult(lib.FFIGlobalFunc):
    def __init__(self) -> None:
        super().__init__("mult")
    
    def __call__(self,x,y):
        return super().__call__(x,y)      
mult = Mult()
result = mult(5,6) #gives 30
print(result)

class CstrTester(lib.FFIGlobalFunc):
    def __init__(self) -> None:
        super().__init__("cstrtester")
    
    def __call__(self, *args):
        return super().__call__(*args)  
    
cstrtester = CstrTester()
result = cstrtester() #gives "good"
print(result)

class Count_Zeros(lib.FFIGlobalFunc):
    def __init__(self) -> None:
        super().__init__("count_zeros")
    
    def __call__(self, array:np.ndarray):
        # the function is actually provided by super().__call__
        # so you could freely wrap the original function
        return super().__call__(array,array.size)  

count_zeros = Count_Zeros()
# note that the dtype has to be correct
array = np.array([1,2,3,4,5,0,0,0],dtype = np.uint32) 
result = count_zeros(array) #gives 3
print(result)