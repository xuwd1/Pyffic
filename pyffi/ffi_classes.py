import ctypes
from . import ffi_common



# descriptor only work when it's binded to classes instead of objects
class FFIClassFieldDescriptor:
    cffi_registered_name = None
    _sigelement_descriptor = None
    _offset = None
    _lib = None
    def __init__(self,cls:type,cffi_registered_name:str) -> None:
        self._lib = cls._lib
        assert not self._lib.typing_manager.ffi_is_basic_type(cls), "invalid type"
        assert cffi_registered_name.startswith(cls.cffi_registered_name), "bad class field definition"
        self.cffi_registered_name = cffi_registered_name
        entry_type = ffi_common.FFIAccessEntryType.kClassField
        access_entry = self._lib.ffi_find_access_entry(entry_type,self.cffi_registered_name)
        self._offset = access_entry.offset
        sig_element = access_entry.sig.decode("utf_8")
        self._sigelement_descriptor = self._lib.typing_manager.ffi_get_sig_element_descriptor(sig_element)
        assert ctypes.sizeof(self._sigelement_descriptor.ctypes_type) == access_entry.field_size
    
    def __get__(self,instance,owner):
        assert(isinstance(instance,self._lib.FFIClassBase))
        instance_ptr = instance._ptr
        field_ptr = instance_ptr+self._offset
        ctypes_object = self._sigelement_descriptor.ctypes_type.from_address(field_ptr)
        if self._sigelement_descriptor.is_basic_type:
            # get value 
            return ctypes_object.value  
        elif self._sigelement_descriptor.is_basic_type_pointer:
            # return ctypes pointer
            return ctypes_object
        else:
            # extended type pointers
            return self._lib.typing_manager.ffi_xtype_to_mapping_entry(
                self._sigelement_descriptor.sig_element
                ).f_ctypes_to_python(ctypes_object.value)

    def __set__(self,instance,value):
        assert(isinstance(instance,self._lib.FFIClassBase))
        assert self._sigelement_descriptor.is_basic_type, "setting pointers is prohibited"
        instance_ptr = instance._ptr
        field_ptr = instance_ptr+self._offset
        ctypes_object = self._sigelement_descriptor.ctypes_type.from_address(field_ptr)
        ctypes.pointer(ctypes_object)[0] = value
            
        

#TODO: MOVE/COPY? IMPLEMENT THEM      

def generate_classbase(lib):
    class _Method_wrapper:
        def __init__(self,obj,mf) -> None:
            self.mf = mf
            self.obj = obj
        def __call__(self, *args):
            return self.mf(self.obj,*args)
            
        
    class FFIClassBase:
        cffi_registered_name = None
        _ptr:int = None
        _constructor = None
        _destructor = None
        _method_callables = None
        _fields = None
        _lib = lib
        _own = False
        
        # __new__的行为：
        # 
        # (1)如果new返回的object类型确实是cls，那么Foo()首先调用new，
        # 将返回的object作为self，再将剩余的参数直接滑入init中
        # 此时new和init的参数数量必须一样（除了cls对应到self)
        # (2)如果new返回的object不是cls，那么Foo()只执行new，然后返回new的返回值
        # use new to create only a python object
        def __new__(cls,*args):
            obj = object.__new__(cls)
            for method_name, method_f in obj._method_callables.items():
                bind_name:str = None
                if hasattr(obj,method_name):
                    bind_name = "_"+method_name
                else:
                    bind_name = method_name
                setattr(obj,bind_name,_Method_wrapper(obj,method_f))
            for field_name, fd in obj._fields.items():
                bind_name:str = None
                if field_name in dir(obj):
                    bind_name = "_"+field_name
                else:
                    bind_name = field_name
                setattr(cls,bind_name,fd)
            return obj
        
        @classmethod
        def create(cls):
            obj = cls.__new__(cls)
            return obj
        
        def __init_subclass__(cls) -> None:
            cffi_typestr = "*"+cls.cffi_registered_name
            cls._fields = {}
            cls._method_callables = {}
            cls._lib.typing_manager.ffi_resolve_extended_type(cffi_typestr,cls)
            cls._lib.typing_manager.ffi_set_f_python_to_ctypes(cffi_typestr,lambda x:x._ptr)
            def f_ctypes_to_python(ptr):
                obj = cls.create()
                obj._ptr = ptr
                return obj
            cls._lib.typing_manager.ffi_set_f_ctypes_to_python(cffi_typestr,f_ctypes_to_python)
            
            # init constructor and destructor
            cls._constructor = cls._lib.FFIConstructor(cls)
            cls._destructor = cls._lib.FFIDestructor(cls)
            # init all class methods 
            entry_num = cls._lib.ffi_get_access_entry_num()
            for i in range(entry_num):
                access_entry = cls._lib.ffi_get_access_entry(i)[0]
                if access_entry.access_type() is ffi_common.FFIAccessEntryType.kClassMethod:
                    method_cffi_registered_name = access_entry.name.decode("utf_8")
                    if method_cffi_registered_name.startswith(cls.cffi_registered_name):
                        method_name = method_cffi_registered_name.split(".")[-1]
                        cls._method_callables[method_name] = \
                            cls._lib.FFIClassMethod(cls,method_cffi_registered_name)
            # TODO: INIT FIELDS
                if access_entry.access_type() is ffi_common.FFIAccessEntryType.kClassField:
                    field_cffi_registered_name = access_entry.name.decode("utf_8")
                    if field_cffi_registered_name.startswith(cls.cffi_registered_name):
                        field_name = field_cffi_registered_name.split(".")[-1]
                        cls._fields[field_name] = \
                            FFIClassFieldDescriptor(cls,field_cffi_registered_name)
        
        #use init to create both python object and cpp object
        def __init__(self,*args) -> None:
            self._own = True
            self._ptr = self._constructor(*args)
            
        def __del__(self):
            if self._ptr is not None and self._own:
                self._destructor(self._ptr)
                
    return FFIClassBase



#class Foo(FFIClassBase):
#    cffi_registered_name = "fooclass"
#    
#    def __init__(self, *args) -> None:
#        super().__init__(*args)
#        
#    def foomf2(self,x,y):
#        # ffi generated _foomf2 for us!
#        return self._foomf2(x,y)
#    
#    @property
#    def field(self):
#        return self._field
#    
#    @field.setter
#    def field(self,value):
#        self._field = value
#    
#
#
#def test_free():
#    foo = Foo(5)
#    foo.field = 10
#    del foo
#
#test_free()

