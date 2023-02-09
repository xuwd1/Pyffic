#pragma once
#include <cstddef>


// a simple compile time concat'able string class 

template <size_t N>
class const_str{
    
    char _array[N+1];
    public:
    constexpr char operator[](size_t index) const{
        return _array[index];
    }
    consteval const_str(const char (&_str)[N+1]){
        for (size_t i=0; i<N+1; i++){
            _array[i] = _str[i];
        }
    }
    template <size_t N1>
    consteval const_str(const const_str<N1>& s1, const const_str<N-N1>& s2){
        for (size_t i=0; i<N1; i++){
            _array[i] = s1[i];
        }
        for (size_t i=0; i<N-N1+1 ;i++){
            _array[i+N1] = s2[i];
        }
    }
    constexpr const char* c_str() const{
        return _array;
    }

};

template <size_t NP1>
consteval auto make_const_str(const char (&s)[NP1]) -> const_str<NP1-1>{
    return const_str<NP1-1>(s);
}

template <size_t N1, size_t N2>
consteval auto operator+(const const_str<N1>& s1, const const_str<N2>& s2)->const_str<N1+N2>{
    return const_str<N1+N2>(s1,s2);
}