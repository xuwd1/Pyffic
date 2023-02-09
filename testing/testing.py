import pyffi
import numpy as np

lib = pyffi.Lib("/home/david/workspace/pywavfile/distribute/pyffic/testing/testlib.so")
lib.ffi_print_all_entries()

class AnaClass(lib.FFIClassBase):
    cffi_registered_name = "anaclass"
    
    def __init__(self, a,b) -> None:
        super().__init__(a,b)
        

class FooClass(lib.FFIClassBase):
    cffi_registered_name = "fooclass"
    
    def __init__(self, spd,cnt) -> None:
        super().__init__(spd,cnt)
    
    def double_speed(self):
        return self._double_speed()
    
    def count_zero(self,array):
        return self._count_zero(array,array.size)
    
    @property
    def speed(self):
        return self._speed
    
    @speed.setter
    def speed(self,value):
        self._speed = value
    
foo = FooClass(10,8)
print(foo.another.a)
nparray = np.array([10,0,0,0,0,2,34,123],dtype=np.uint32)
foo.count_zero(nparray)
