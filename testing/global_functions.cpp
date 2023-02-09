#include "../cpp/ffi_man.hpp"
#include <cstdint>
#include <cstddef>

double mult(double x, double y){
    return x*y;
}
FFI_REGISTER_GLOBAL_FUNCTION(mult, "mult");

const char* cstrtester(){
    static const char* str = "good";
    return str;
}
FFI_REGISTER_GLOBAL_FUNCTION(cstrtester, "cstrtester");

uint64_t count_zeros(uint32_t* array, uint64_t n){
    uint64_t count = 0;
    for (uint64_t i=0;i<n;i++){
        if (array[i]==0) count++;
    }
    return count;
}
FFI_REGISTER_GLOBAL_FUNCTION(count_zeros, "count_zeros");