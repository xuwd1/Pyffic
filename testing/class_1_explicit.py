#Python side code
import pyffi

# this is the ffi manager instance for class_1.so
lib = pyffi.Lib("./class_1.so")
class FooClass(lib.FFIClassBase):
    # you have to provide cffi_registered_name manually
    cffi_registered_name = "fooclass"
    def __init__(self, spd,cnt) -> None:
        super().__init__(spd,cnt)
        
    def double_speed(self):
        # since attr "double_speed" already exists
        # pyffi now binds the method with a prefix
        return self._double_speed()
    
    @property
    def speed(self):
        # same for class fields
        return self._speed
    
    @speed.setter
    def speed(self,value):
        self._speed = value

foo = FooClass(100,5)
print("foo's speed is {}".format(foo.speed))
foo.speed = 789
print("foo's new speed is {}".format(foo.speed))
foo.double_speed()
print("foo's doubled new speed is {}".format(foo.speed))