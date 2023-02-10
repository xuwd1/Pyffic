#include "../cpp/ffi_man.hpp"
#include <cstdio>
#include <cstdint>

class anotherclass{
public:
    anotherclass(uint32_t a, uint32_t b):a(a),b(b){}
    uint32_t a;
    uint32_t b;
};

anotherclass* create_anaclass(uint32_t a, uint32_t b){
    auto ptr = new anotherclass(a,b);
    std::printf("created anotherclass!\n");
    return ptr;
}

void destroy_anaclass(anotherclass* ptr){
    delete ptr;
    printf("deleted anotherclass\n");
}

FFI_REGISTER_CLASS(anotherclass, "anotherclass", create_anaclass, destroy_anaclass)
FFI_REGISTER_CLASS_FIELD(anotherclass, a, anotherclass::a, "anotherclass.a")


class fooclass{
public:
    fooclass(uint32_t a, uint32_t b){
        other = new anotherclass(a,b);
    }
    ~fooclass(){
        delete other;
    }
    anotherclass* other;
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
FFI_REGISTER_CLASS_FIELD(fooclass, other, fooclass::other, "fooclass.other")
