#include "../cpp/ffi_man.hpp"
#include <cstdio>
#include <cstdint>


class fooclass{
public:
    fooclass(float spd, int cnt):speed(spd),count(cnt){
    }
    ~fooclass(){
    }
    void double_speed(){
        speed = speed*2;
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
FFI_REGISTER_CLASS_FIELD(fooclass, speed, fooclass::speed, "fooclass.speed");
FFI_REGISTER_CLASS_METHOD(&fooclass::double_speed, "fooclass.double_speed");
