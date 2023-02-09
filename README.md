# Pyffic
## Table of Contents
- [Pyffic](#pyffic)
  - [Table of Contents](#table-of-contents)
  - [What is Pyffic?](#what-is-pyffic)
  - [Requirements](#requirements)
  - [Usage](#usage)
    - [Cpp Side Preparations](#cpp-side-preparations)
    - [Python Side Preparations](#python-side-preparations)
    - [Global Functions](#global-functions)
    - [Classes](#classes)
  - [Limitations](#limitations)

## What is Pyffic?
Pyffic is a simple yet useful Cpp-Python FFI (Foreign Function Interface) system. Pyffic consists of two components: **ffi_man** on Cpp side and **pyffi** on Python side. 

**ffi_man** allows you to[^1]: 

1. Register global functions by recording their registered names, addresses, and generating compile time strings that represent the functions' signatures. (for example, a Cpp function declared as `uint32_t func(fooclass* ptr, int8_t)` corresponds to a compile time signature string `":*fooclass:i8;u32"`.) When your Cpp programs are compiled to shared libs, these information could help external programs that load the shared libs know how the functions could be called under specific ABI, avoiding the Cpp name mangling problem.
2. Register custom Cpp classes by recording their registered name, constructor, and destructor. (for example, registering a class named `fooclass` by using macro `FFI_REGISTER_CLASS(fooclass, "fooclass", create_fooclass, destroy_fooclass);`) These information could help external programs written in different language to create the Cpp classes' counterpart objects. Besides, the registered name of the Cpp class could also be used to generate compile time function signature mentioned in 1.
3. Register custom Cpp class fields by recording their registered name, offset, and compile time type string. (for example, registering a class field `fooclass::speed` by using macro `FFI_REGISTER_CLASS_FIELD(fooclass, speed, fooclass::speed, "fooclass.speed");`) These information could help external programs to access or modify the class value.
4. Register custom Cpp class methods by generating method wrappers, recording wrapper signatures, and wrapper addresses. (for example, registering a class method `fooclass::double_speed` by using macro `FFI_REGISTER_CLASS_METHOD(&fooclass::double_speed, "fooclass.double_speed");`) These information could help external programs to call the class methods.

[^1]: from the above statements you could see that **ffi_man** could also be used to establish a FFI system other than a Python-Cpp one.

**pyffi** allows you to:

1. Easily define a Cpp global function counterpart in Python, by automatically reading the **ffi_man**'s recorded information and performing argument conversion, function calling and return value conversion.
2. Easily define a Cpp class counterpart in Python, by automatically reading the **ffi_man**'s recorded information, creating proper Python `__init__` function, `__del__` function, normal class methods and descriptors that handle class field accesses.


## Requirements
- On Cpp side, pyffic requires a modern compiler that supports C++20 standard (e.g. clang14 and higher) to work 
  - This is because **ffi_man** used some C++20 specifiers such as `consteval`. Actually its core functionalities only require C++14 to work. 
- On Python side, pyffic requires python >= 3.6, and numpy
  -  Because for **pyffi** to work it requires `__init_subclass__` magic method, which is available only in python >= 3.6
  -  Because for a Cpp function/method that has pointer parameters, **pyffi** would expect  `numpy.ndarray`s as argument

## Usage
### Cpp Side Preparations

1. Include `path/to/Pyffic/cpp/ffi_man.hpp` in your Cpp source files. Note that `ffi_man.hpp` will include all the header files under `path/to/Pyffic/cpp/siggen` so you also would need to ensure that your compiler could find them. It is recommended to keep the directory structure of `Pyffic/cpp` for convenience.
2. Add `path/to/Pyffic/cpp/ffi_man.cpp` to your Cpp source file list.

### Python Side Preparations

1. Add `path/to/Pyffic/pyffi` to your `$PYTHONPATH` to allow your Python interpreter find **pyffi**
2. If you use Python environment manager like `conda`, make sure that your environment interpreter could find **pyffi**
3. Test if `import pyffi` is working


### Global Functions
**1. normal global functions**
```cpp
//Cpp side code that compiles to lib.so
#include "ffi_man.hpp"

double mult(double x, double y){
    return x*y;
}
FFI_REGISTER_GLOBAL_FUNCTION(mult, "mult");
```
```python
#Python side code
import pyffi

# this is the ffi manager instance for lib.so
lib = pyffi.Lib("lib.so")
class Mult(lib.FFIGlobalFunc):
    def __init__(self) -> None:
        super().__init__("mult")
    
    def __call__(self,x,y):
        return super().__call__(x,y)      
mult = Mult()
result = mult(5,6) #gives 30
```

**2. functions returning strings**
```cpp
//Cpp side code that compiles to lib.so
#include "ffi_man.hpp"

const char* cstrtester(){
    static const char* str = "good";
    return str;
}
FFI_REGISTER_GLOBAL_FUNCTION(cstrtester, "cstrtester");
```
```python
#Python side code
import pyffi

# this is the ffi manager instance for lib.so
lib = pyffi.Lib("lib.so")
class CstrTester(lib.FFIGlobalFunc):
    def __init__(self) -> None:
        super().__init__("cstrtester")
    
    def __call__(self, *args):
        return super().__call__(*args)  
    
cstrtester = CstrTester()
result = cstrtester() #gives "good"
```

**3. functions accepting pointer arguments**
```cpp
//Cpp side code that compiles to lib.so
#include "ffi_man.hpp"

uint64_t count_zeros(uint32_t* array, uint64_t n){
    uint64_t count = 0;
    for (uint64_t i=0;i<n;i++){
        if (array[i]==0) count++;
    }
    return count;
}
FFI_REGISTER_GLOBAL_FUNCTION(count_zeros, "count_zeros");
```
Note that pyffi would always expect a numpy.ndarray object for Cpp pointer parameters!
```python
#Python side code
import pyffi
import numpy as np

# this is the ffi manager instance for lib.so
lib = pyffi.Lib("lib.so")
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
```

### Classes
**1.Class constructor and destructor**
```cpp
//Cpp side code that compiles to lib.so
#include "ffi_man.hpp"
class fooclass{
public:
    fooclass(float spd, int cnt):speed(spd),count(cnt){
    }
    ~fooclass(){
    }
    float speed;
    int count;
};

// in Cpp getting constructor/destructor addr is strictly prohibited
// so we have to wrap them ourselves. 
fooclass* create_fooclass(float spd, int cnt){
    auto ptr = new fooclass(spd,cnt);
    std::printf("created fooclass!\n");
    return ptr;
}

void destroy_fooclass(fooclass* fc){
    delete fc;
    printf("deleted fooclass\n");
}

FFI_REGISTER_CLASS(fooclass, "fooclass", create_fooclass, destroy_fooclass);
```
```python
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
# running the script gives 
# created fooclass!
# deleted fooclass
```

To be Continued in the following commits.

You could also check `Pyffic/testing`.


## Limitations
To be written...