#include <functional>

/*
we now use this member function wrapper generator template
*/


template <size_t N ,typename Cl, typename Func>
struct _mf_helper;

template <size_t N ,typename Cl, typename R,typename... Args>
struct _mf_helper<N,Cl,R(Args...)>{
    // type define R(Cl::*)(Args...) to Clmemfunctionptr
    typedef R (Cl::*Clmemfunctionptr)(Args...);
    // constructor: set _funcptr to given member function pointer
    _mf_helper<Cl, R(Args...)>(Clmemfunctionptr func){
        _funcptr = func;
    }
    static inline Clmemfunctionptr _funcptr;
    // final target: define a wrapper function ...
    static R wrapper_function(Cl* cl,Args... args){
        // ... whose evaluation invokes stored member function pointer _funcptr
        return std::invoke(_funcptr,cl, args...);
    }
};


// struct responsible for wrapping a member function
// primary template
// note that template parameter N is needed for generating warppers of 
// different types to wrap member functions with the same type T!
// you could simply pass a __COUNTER__ macro to it
template <size_t N, typename T>
struct mf_wrapper;

template <size_t N, typename Cl, typename Func>
struct mf_wrapper<N,Func(Cl::*)>:_mf_helper<N,Cl, Func>{
    typedef Func(Cl::*_memfp_type);
    mf_wrapper<N,Func(Cl::*)>(_memfp_type ptr):_mf_helper<N,Cl, Func>(ptr){}
};

template <size_t N, typename Cl, typename Func>
// this template funtion returns a mf_wrapper object that wraps the given member function
//                                      \/ member function pointer called "member_function_ptr"                                           
mf_wrapper<N,Func(Cl::*)> make_mf_wrapper(Func(Cl::*member_function_ptr)){
    return mf_wrapper<N,Func(Cl::*)>(member_function_ptr);
}

// use wrapped_memf_type<decltype(fooclass::foo)>::type to get wrapper function type!
template <typename Cl, typename Func> 
struct wrapped_memf_type_impl_;
template <typename Cl, typename R,typename... Args>
struct wrapped_memf_type_impl_<Cl,R(Args...)>{
    using type = R(Cl*,Args...);
};

template<typename T>
struct wrapped_memf_type;
template <typename Cl, typename Func>
struct wrapped_memf_type<Func(Cl::*)>:wrapped_memf_type_impl_<Cl, Func> {};



