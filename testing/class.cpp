#include "../cpp/ffi_man.hpp"
#include <cstdio>
#include <cstdint>

class fooclass{
public:
    fooclass(float spd, int cnt):speed(spd),count(cnt){
    }
    ~fooclass(){
    }
    //void count_zero(uint32_t* array, size_t n){
    //    count = 0;
    //    for (size_t i=0; i<n; i++){
    //        if (array[i]==0){
    //            count++;
    //        }
    //    }
    //}
    //float double_speed(){
    //    return speed*2;
    //}
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
