#Python side code
import pyffi

# this is the ffi manager instance for class_2.so
lib = pyffi.Lib("./class_2.so")
class FooClass(lib.FFIClassBase):
    # you have to provide cffi_registered_name manually
    cffi_registered_name = "fooclass"
    def __init__(self, a,b) -> None:
        super().__init__(a,b)
        
class AnotherClass(lib.FFIClassBase):
    cffi_registered_name = "anotherclass"
    def __init__(self, a,b) -> None:
        super().__init__(a,b)


foo = FooClass(6,7)
print(foo.other)
print(foo.other.a)


