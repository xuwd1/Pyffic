import ctypes
from enum import Enum
from . import ffi_common
from . import ffi_typing
from . import ffi_callables
from . import ffi_classes


class FFIAccessEntry(ctypes.Structure):
    _fields_ = [
        ("type",ctypes.c_int),
        ("ptr",ctypes.c_void_p),
        ("name",ctypes.c_char_p),
        ("sig",ctypes.c_char_p),
        ("offset",ctypes.c_size_t),
        ("field_size",ctypes.c_size_t)
    ]
    def access_type(self)->ffi_common.FFIAccessEntryType:
        return ffi_common.FFIAccessEntryType(self.type)
        
class FFIClassEntry(ctypes.Structure):
    _fields_ = [
        ("class_namestr",ctypes.c_char_p),
        ("construct_func_ptr",ctypes.c_void_p),
        ("construct_func_sig",ctypes.c_char_p),
        ("destroy_func_ptr",ctypes.c_void_p),
        ("destroy_func_sig",ctypes.c_char_p)
    ]
    
    
class Lib:
    def __init__(self,lib_path:str) -> None:
        self.lib = ctypes.CDLL(lib_path)
        self.typing_manager = ffi_typing.FFITypingManager(self)
        gf,cm,ct,dt = ffi_callables.generate_callables(self)
        self.FFIGlobalFunc=gf
        self.FFIClassMethod=cm
        self.FFIConstructor=ct
        self.FFIDestructor=dt
        self.FFIClassBase=ffi_classes.generate_classbase(self)
        #setattr(self,"FFIGlobalFunc",gf)
        #setattr(self,"FFIClassMethod",cm)
        #setattr(self,"FFIConstructor",ct)
        #setattr(self,"FFIDestructor",dt)
        

    def ffi_get_access_entry_num(self):
        self.lib.ffi_get_access_entry_num.restype = ctypes.c_ulong
        self.lib.ffi_get_access_entry_num.argtypes = []
        return self.lib.ffi_get_access_entry_num()

    def ffi_get_access_entry(self,index):
        self.lib.ffi_get_access_entry.restype = ctypes.POINTER(FFIAccessEntry)
        self.lib.ffi_get_access_entry.argtypes = [ctypes.c_ulong]
        return self.lib.ffi_get_access_entry(index)

    def ffi_find_access_entry(self,entry_type:ffi_common.FFIAccessEntryType, cffi_registered_name:str)->FFIAccessEntry:
        entry_count = self.ffi_get_access_entry_num()
        for i in range(entry_count):
            entry = self.ffi_get_access_entry(i)[0]
            if entry.access_type() is not entry_type:
                continue
            entry_name = entry.name.decode("utf_8")
            if entry_name == cffi_registered_name:
                return entry
        return None
        
    def ffi_get_class_entry_num(self):
        self.lib.ffi_get_class_entry_num.restype = ctypes.c_ulong
        self.lib.ffi_get_class_entry_num.argtypes = []
        return self.lib.ffi_get_class_entry_num()

    def ffi_get_class_entry(self,index):
        self.lib.ffi_get_class_entry.restype = ctypes.POINTER(FFIClassEntry)
        self.lib.ffi_get_class_entry.argtypes = [ctypes.c_ulong]
        return self.lib.ffi_get_class_entry(index)

    def ffi_find_class_entry(self,cffi_registered_name:str):
        entry_count = self.ffi_get_class_entry_num()
        for i in range(entry_count):
            entry = self.ffi_get_class_entry(i)[0]
            class_name = entry.class_namestr.decode("utf_8")
            if class_name == cffi_registered_name:
                return entry
        return None

    def ffi_print_all_entries(self):
        self.lib.ffi_print_all_entries()








