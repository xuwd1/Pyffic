#Python side code
import pyffi

# this is the ffi manager instance for lib.so
lib = pyffi.Lib("./class.so")
class FooClass(lib.FFIClassBase):
    # you have to provide cffi_registered_name manually
    cffi_registered_name = "fooclass"
    def __init__(self, spd,cnt) -> None:
        super().__init__(spd,cnt)

foo = FooClass(100,5)