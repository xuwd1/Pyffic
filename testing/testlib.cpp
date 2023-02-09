#include "../cpp/ffi_man.hpp"
#include <cstdio>
#include <cstdint>

//CLASS TESTS

class anaclass{
public:
    anaclass(uint32_t a, uint32_t b):a(a),b(b){}
    uint32_t a;
    uint32_t b;
};

anaclass* create_anaclass(uint32_t a, uint32_t b){
    auto ptr = new anaclass(a,b);
    std::printf("created anaclass!\n");
    return ptr;
}

void destroy_anaclass(anaclass* ptr){
    delete ptr;
    printf("deleted anaclass\n");
}

FFI_REGISTER_CLASS(anaclass, "anaclass", create_anaclass, destroy_anaclass);
FFI_REGISTER_CLASS_FIELD(anaclass, a, anaclass::a, "anaclass.a");
FFI_REGISTER_CLASS_FIELD(anaclass, b, anaclass::b, "anaclass.b");


class fooclass{
public:
    fooclass(float spd, int cnt):speed(spd),count(cnt){
        another = new anaclass(999,888);
        printf("%ld\n",another);
        printf("%d\n",*another);
        printf("%d\n",*(reinterpret_cast<uint8_t*>(another)+4));
        printf("%d\n",another->a);
        printf("%d\n",another->b);
    }
    ~fooclass(){
        delete another;
    }
    void count_zero(uint32_t* array, size_t n){
        count = 0;
        for (size_t i=0; i<n; i++){
            if (array[i]==0){
                count++;
            }
        }
    }
    float double_speed(){
        return speed*2;
    }
    anaclass* another;
    float speed;
    int count;
};

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
FFI_REGISTER_CLASS_METHOD(&fooclass::count_zero, "fooclass.count_zero");
FFI_REGISTER_CLASS_METHOD(&fooclass::double_speed, "fooclass.double_speed");
FFI_REGISTER_CLASS_FIELD(fooclass, speed, fooclass::speed, "fooclass.speed");
FFI_REGISTER_CLASS_FIELD(fooclass, count, fooclass::count, "fooclass.count");
FFI_REGISTER_CLASS_FIELD(fooclass, another, fooclass::another, "fooclass.another");
