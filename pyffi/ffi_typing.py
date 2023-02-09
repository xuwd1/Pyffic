import ctypes
from enum import Enum
import numpy as np
from typing import Set

class FFITypeMappingType(Enum):
    kBasic = 1,
    kExtended = 2

class FFITypeMappingEntry:
    def __init__(self,
                 c_ffi_type_str,
                 ctypes_type,
                 python_type,
                 mapping_type = FFITypeMappingType.kBasic,
                 f_ctypes_to_python = None,
                 f_python_to_ctypes = None):
        self.c_ffi_type_str = c_ffi_type_str
        self.ctypes_type = ctypes_type
        self.python_type = python_type
        self.mapping_type = mapping_type
        # function for converting ctype CFUNC retvalue to actual python type
        self.f_ctypes_to_python = f_ctypes_to_python
        # function for converting python type to ctypes accepted argtype
        self.f_python_to_ctypes = f_python_to_ctypes


    
        
        
class FFITypeMapping:
    entries = [
        FFITypeMappingEntry(
            c_ffi_type_str = "i8",
            ctypes_type=ctypes.c_int8,
            python_type=int
        ),
        FFITypeMappingEntry(
            c_ffi_type_str = "u8",
            ctypes_type=ctypes.c_uint8,
            python_type=int
        ),
        FFITypeMappingEntry(
            c_ffi_type_str = "i16",
            ctypes_type=ctypes.c_int16,
            python_type=int
        ),
        FFITypeMappingEntry(
            c_ffi_type_str = "u16",
            ctypes_type=ctypes.c_uint16,
            python_type=int
        ),
        FFITypeMappingEntry(
            c_ffi_type_str = "i32",
            ctypes_type=ctypes.c_int32,
            python_type=int
        ),
        FFITypeMappingEntry(
            c_ffi_type_str = "u32",
            ctypes_type=ctypes.c_uint32,
            python_type=int
        ),
        FFITypeMappingEntry(
            c_ffi_type_str = "i64",
            ctypes_type=ctypes.c_int64,
            python_type=int
        ),
        FFITypeMappingEntry(
            c_ffi_type_str = "u64",
            ctypes_type=ctypes.c_uint64,
            python_type=int
        ),
        FFITypeMappingEntry(
            c_ffi_type_str = "f32",
            ctypes_type=ctypes.c_float,
            python_type=float
        ),
        FFITypeMappingEntry(
            c_ffi_type_str = "f64",
            ctypes_type=ctypes.c_double,
            python_type=float
        ),
        FFITypeMappingEntry(
            c_ffi_type_str = "void",  #void only shows up in rettype sig
            ctypes_type=None,
            python_type=None,
        ),
        FFITypeMappingEntry(
            c_ffi_type_str = "*cstr",
            ctypes_type=ctypes.c_char_p,
            python_type=str,
            mapping_type=FFITypeMappingType.kExtended,
            f_ctypes_to_python=lambda x:x.decode("utf_8"),
            f_python_to_ctypes=lambda x:x.encode("utf_8")
        ),
        FFITypeMappingEntry(
            c_ffi_type_str= None,
            ctypes_type= None,
            python_type= np.ndarray,
            mapping_type=FFITypeMappingType.kExtended,
            f_ctypes_to_python=None,
            f_python_to_ctypes=np.ctypeslib.as_ctypes
        )
        
        
    ]
    dict_cffi_to_entry = {}
    dict_ctypes_to_entry = {} 
    dict_pythontype_to_entry = {}
    cffi_basictypes:Set = None
    python_basictypes:Set = None
    lib = None
    
    def __init__(self,lib) -> None:
        self.lib = lib
        self._build_basic_types()
        self._init_class_mappings()
        self._update_dict()
    
    
    def _init_class_mappings(self):
        entry_count = self.lib.ffi_get_class_entry_num()
        for i in range(entry_count):
            entry = self.lib.ffi_get_class_entry(i)[0]
            class_name = entry.class_namestr.decode("utf_8")
            # class names with the same name as basic types are not allowed
            assert class_name not in self.cffi_basictypes, "invalid class name"
            new_entry = FFITypeMappingEntry(
                c_ffi_type_str="*"+class_name,
                ctypes_type=ctypes.c_void_p,
                python_type=None,
                mapping_type=FFITypeMappingType.kExtended
            )
            self.entries.append(new_entry)  
    
    
    def _build_basic_types(self):
        cffi_basic = []
        python_basic = []
        for entry in self.entries:
            if entry.c_ffi_type_str is not None:
                if entry.mapping_type is FFITypeMappingType.kBasic:
                    cffi_basic.append(entry.c_ffi_type_str)
            if entry.python_type is not None:
                if entry.mapping_type is FFITypeMappingType.kBasic:
                    python_basic.append(entry.python_type)
        self.cffi_basictypes = set(cffi_basic)
        self.python_basictypes = set(python_basic)
    
            
    def _update_dict(self):
        # todo: optimizations needed 
        for ent in self.entries:
            if ent.c_ffi_type_str is not None:  
                self.dict_cffi_to_entry[ent.c_ffi_type_str] = ent
            if ent.ctypes_type is not None: 
                self.dict_ctypes_to_entry[ent.ctypes_type] = ent
            if ent.python_type is not None:
                self.dict_pythontype_to_entry[ent.python_type] = ent
    
        
        
    
class SigElementDescriptor:
    indirection_level = None
    ctypes_type = None
    sig_element = None
    sig_element_removed_indirection = None
    is_basic_type_pointer = None
    is_basic_type = None
    def __init__(self,
                    indirection_level,
                    ctypes_type,
                    sig_element,
                    sig_element_removed_indirection,
                    is_basic_type_pointer,
                    is_basic_type
                    ) -> None:
        self.indirection_level = indirection_level
        self.ctypes_type = ctypes_type
        self.sig_element = sig_element
        self.sig_element_removed_indirection = sig_element_removed_indirection,
        self.is_basic_type_pointer = is_basic_type_pointer
        self.is_basic_type = is_basic_type


class FFITypingManager:
    def __init__(self,lib) -> None:
        self.lib = lib
        self.S_FFITypeMapping = FFITypeMapping(self.lib)
    
    
    def ffi_is_basic_type(self,ty:str|object):
        if isinstance(ty,str):
            if ty in self.S_FFITypeMapping.cffi_basictypes:
                return True
        else:
            if ty in self.S_FFITypeMapping.python_basictypes:
                return True
        return False
    
    def ffi_resolve_extended_type(self,cffi_type_str:str,ty:type):
        entry = self.ffi_xtype_to_mapping_entry(cffi_type_str)
        assert entry.python_type is None, "resetting extend type mapping"
        entry.python_type = ty
        self.S_FFITypeMapping._update_dict()
        
    
    def ffi_set_f_python_to_ctypes(self,cffi_type_str:str,f_python_to_ctypes):
        entry = self.ffi_xtype_to_mapping_entry(cffi_type_str)
        assert entry is not None, "no valid entry found"
        entry.f_python_to_ctypes = f_python_to_ctypes

    def ffi_set_f_ctypes_to_python(self,cffi_type_str:str,f_ctypes_to_python):
        entry = self.ffi_xtype_to_mapping_entry(cffi_type_str)
        assert entry is not None, "no valid entry found"
        entry.f_ctypes_to_python = f_ctypes_to_python



    def ffi_xtype_to_mapping_entry(self,ty:str|object)->FFITypeMappingEntry:
        if isinstance(ty,str):
            return self.S_FFITypeMapping.dict_cffi_to_entry[ty]
        elif isinstance(ty,type(ctypes.c_int)):
            return self.S_FFITypeMapping.dict_ctypes_to_entry[ty]
        else:
            if ty in self.S_FFITypeMapping.python_basictypes:
                raise ValueError("python basic types encountered")
            else:
                assert ty in self.S_FFITypeMapping.dict_pythontype_to_entry, "unresolved type encountered"
                return self.S_FFITypeMapping.dict_pythontype_to_entry[ty]


    def ffi_get_sig_element_descriptor(self,sig_element:str):
        indirection_level = sig_element.count('*')
        assert indirection_level <= 1, "exceeded maximum allowed indirection level"
        sige_removed_indirection = sig_element[indirection_level:]
        ri_is_basic = self.ffi_is_basic_type(sige_removed_indirection)
        if ri_is_basic:
            ctypes_type = self.ffi_xtype_to_mapping_entry(sige_removed_indirection).ctypes_type
            if indirection_level != 0:
                ctypes_type = ctypes.POINTER(ctypes_type)
        else:
            assert indirection_level != 0, "only pointer types to extendedtype allowed"
            ctypes_type = self.ffi_xtype_to_mapping_entry(sig_element).ctypes_type
        return SigElementDescriptor(
            indirection_level,
            ctypes_type,
            sig_element,
            sige_removed_indirection,
            indirection_level == 1 and ri_is_basic,
            indirection_level == 0 and ri_is_basic
        )
        

    def ffi_generate_ctypes_type_from_sig_element(self,sig_element:str):
        sd = self.ffi_get_sig_element_descriptor(sig_element)
        return sd.ctypes_type

    def ffi_split_sig_to_element(self,sig:str):
        assert sig.count(";")!=0, "invalid sig"
        args,ret = sig.split(";")
        r = [ret]
        if len(args)==0:
            return r
        else:
            for arg in args.split(":")[1:]:
                r.append(arg)
        return r
        

