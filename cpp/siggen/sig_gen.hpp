#pragma once
#include <cstddef>
#include <cstdint>
#include <type_traits>
#include "const_str.hpp"
#include "type_attrs.hpp"



/*
legacy code:
signature generation for member function
member function pointer int fooclass::foo(int,float) has type 
"int (fooclass::*)(int,float)"
but it matches to template <Func(Cls::*)>!
where Func = int(int,float)
Cls = fooclass

*/


//template <typename Cl, typename Func>
//struct _memf_helper;
//
//template <typename Func, typename Cl>
//// Func is of a normal function type, while Cl::* is the class member pointer!
//struct signature<Func(Cl::*)>{
//    static constexpr auto sig = _memf_helper<Cl, Func>::sig;
//};
//
//template <typename Cl, typename R,typename... Args>
//struct _memf_helper<Cl,R(Args...)>{
//    static constexpr auto sig = signature<R(Cl*,Args...)>::sig;
//};


template <typename T>
struct signature;

template <typename R, typename Argl, typename... Args>
struct signature<R(Argl,Args...)>{
    static constexpr auto sig = make_const_str(":")+type_str<Argl>::str+signature<R(Args...)>::sig;
    
};

template <typename R, typename Argl>
struct signature<R(Argl)>{
    static constexpr auto sig = make_const_str(":")+type_str<Argl>::str+signature<R()>::sig;
};

template <typename R>
struct signature<R()>{
    static constexpr auto sig = make_const_str(";")+type_str<R>::str;
};

