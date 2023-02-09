import ctypes
from . import ffi_common
import numpy as np

def generate_callables(lib):
    class FFICallableBase:
        sig_elements = None
        ctypes_sig = None
        func = None
        cffi_registered_name = None
        _lib = lib
        def __init__(self) -> None:
            raise NotImplementedError
                
        def __call__(self, *args,**kwargs):
            ctypes_accepted_args = [None]* len(args)
            for i,arg in enumerate(args):
                sd = self._lib.typing_manager.ffi_get_sig_element_descriptor(self.sig_elements[i+1])
                if self._lib.typing_manager.ffi_is_basic_type(type(arg)):
                    ctypes_accepted_args[i] = arg
                    assert sd.is_basic_type or not sd.is_basic_type_pointer, \
                        "passing raw pointers is prohibited"
                else:
                    cmp_str:str = None
                    mapping_entry = self._lib.typing_manager.ffi_xtype_to_mapping_entry(type(arg))
                    if isinstance(arg,np.ndarray):
                        array_ctypes_type = np.ctypeslib.as_ctypes_type(arg.dtype) 
                        cmp_str = "*" + self._lib.typing_manager.ffi_xtype_to_mapping_entry(array_ctypes_type).c_ffi_type_str
                    else:  
                        cmp_str = mapping_entry.c_ffi_type_str
                    assert cmp_str == self.sig_elements[i+1], "argument type error"
                    ctypes_accepted_args[i] = \
                        mapping_entry.f_python_to_ctypes(
                            arg
                        )
                    
            ctypes_retval = self.func(*ctypes_accepted_args)
            if "rt_convert" not in kwargs or not kwargs["rt_convert"]:
                return ctypes_retval
            retval_sig_element = self.sig_elements[0]
            sd = self._lib.typing_manager.ffi_get_sig_element_descriptor(retval_sig_element)
            if sd.is_basic_type:
                # returning basic types: i8,i32... ctypes has done the job for us
                return ctypes_retval
            elif sd.is_basic_type_pointer:
                # returning basic type pointers: *i8... create ctype pointers
                return sd.ctypes_type(ctypes_retval)
            else:
                # returning extended type pointers: need to instantiate its python side counterpart class
                return self._lib.typing_manager.ffi_xtype_to_mapping_entry(retval_sig_element).f_ctypes_to_python(ctypes_retval)


    class FFIGlobalFunc(FFICallableBase):
        def __init__(self,cffi_registered_name:str) -> None:
            self.cffi_registered_name = cffi_registered_name
            entry_type = ffi_common.FFIAccessEntryType.kGlobalFunc
            access_entry = self._lib.ffi_find_access_entry(entry_type,self.cffi_registered_name)
            assert access_entry is not None, "No valid entry found"
            self.sig_elements = self._lib.typing_manager.ffi_split_sig_to_element(access_entry.sig.decode("utf_8"))
            self.ctypes_sig = [None] * len(self.sig_elements)
            for i, sig_element in enumerate(self.sig_elements):
                ctypes_type = self._lib.typing_manager.ffi_get_sig_element_descriptor(sig_element).ctypes_type
                self.ctypes_sig[i] = ctypes_type
            func_maker = ctypes.CFUNCTYPE(*self.ctypes_sig)
            self.func = func_maker(access_entry.ptr)
            
        def __call__(self, *args):
            return super().__call__(*args,rt_convert=True)
    
    class FFIClassMethod(FFICallableBase):
        def __init__(self,cls:type,cffi_registered_name:str) -> None:
            assert not self._lib.typing_manager.ffi_is_basic_type(cls), "invalid type"
            assert cffi_registered_name.startswith(cls.cffi_registered_name), "bad class method definition"
            self.cffi_registered_name = cffi_registered_name
            entry_type = ffi_common.FFIAccessEntryType.kClassMethod
            access_entry = self._lib.ffi_find_access_entry(entry_type,self.cffi_registered_name)
            self.sig_elements = self._lib.typing_manager.ffi_split_sig_to_element(access_entry.sig.decode("utf_8"))
            self.ctypes_sig = [None] * len(self.sig_elements)
            for i, sig_element in enumerate(self.sig_elements):
                ctypes_type = self._lib.typing_manager.ffi_get_sig_element_descriptor(sig_element).ctypes_type
                self.ctypes_sig[i] = ctypes_type
            func_maker = ctypes.CFUNCTYPE(*self.ctypes_sig)
            self.func = func_maker(access_entry.ptr)   
        
        def __call__(self, *args):
            return super().__call__(*args,rt_convert=True)
    
    class FFIConstructor(FFICallableBase):
        def __init__(self,cls:type) -> None:
            assert not self._lib.typing_manager.ffi_is_basic_type(cls), "invalid type"
            self.cffi_registered_name = cls.cffi_registered_name + "_constructor"
            class_entry = self._lib.ffi_find_class_entry(cls.cffi_registered_name)
            assert class_entry is not None, "No valid entry found"
            self.sig_elements = self._lib.typing_manager.ffi_split_sig_to_element(class_entry.construct_func_sig.decode("utf_8"))
            self.ctypes_sig = [None] * len(self.sig_elements)
            for i, sig_element in enumerate(self.sig_elements):
                ctypes_type = self._lib.typing_manager.ffi_get_sig_element_descriptor(sig_element).ctypes_type
                self.ctypes_sig[i] = ctypes_type
            func_maker = ctypes.CFUNCTYPE(*self.ctypes_sig)
            self.func = func_maker(class_entry.construct_func_ptr)
        
        def __call__(self, *args):
            return super().__call__(*args)

    class FFIDestructor(FFICallableBase):
        def __init__(self,cls:type) -> None:
            assert not self._lib.typing_manager.ffi_is_basic_type(cls), "invalid type"
            self.cffi_registered_name = cls.cffi_registered_name + "_destructor"
            class_entry = self._lib.ffi_find_class_entry(cls.cffi_registered_name)
            assert class_entry is not None, "No valid entry found"
            self.sig_elements = self._lib.typing_manager.ffi_split_sig_to_element(class_entry.destroy_func_sig.decode("utf_8"))
            self.ctypes_sig = [None] * len(self.sig_elements)
            for i, sig_element in enumerate(self.sig_elements):
                ctypes_type = self._lib.typing_manager.ffi_get_sig_element_descriptor(sig_element).ctypes_type
                self.ctypes_sig[i] = ctypes_type
            func_maker = ctypes.CFUNCTYPE(*self.ctypes_sig)
            self.func = func_maker(class_entry.destroy_func_ptr)
        
        def __call__(self, *args):
            return super().__call__(*args)
        
    return FFIGlobalFunc,FFIClassMethod,FFIConstructor,FFIDestructor





#class Mult(FFIGlobalFunc):
#    def __init__(self) -> None:
#        super().__init__("mult")
#    
#    def __call__(self, *args):
#        return super().__call__(*args)    
#            
#mult = Mult()
#
#
#class Instant(FFIGlobalFunc):
#    def __init__(self) -> None:
#        super().__init__("instant")
#    
#    def __call__(self, *args):
#        return super().__call__(*args)    
#            
#instant = Instant()
#
#class VoidpTester(FFIGlobalFunc):
#    def __init__(self) -> None:
#        super().__init__("voidptester")
#    
#    def __call__(self, *args):
#        return super().__call__(*args)  
#        
#voidptester = VoidpTester()
#
#class modifyarray(FFIGlobalFunc):
#    def __init__(self) -> None:
#        super().__init__("modify_array")
#    
#    def __call__(self, *args):
#        return super().__call__(*args)  
#        
#modify_array = modifyarray()
#
#class CstrTester(FFIGlobalFunc):
#    def __init__(self) -> None:
#        super().__init__("cstrtester")
#    
#    def __call__(self, *args):
#        return super().__call__(*args)  
#    
#cstrtester = CstrTester()
   



#class fo:
#    def __init__(self) -> None:
#        return 
#
#if __name__ == "__main__":
#   # x = voidptester()
#    y = np.array([1,2,3,4,5],dtype=np.uint32)
#    modify_array(y)
#    a=1