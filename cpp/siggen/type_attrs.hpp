#pragma once
#include <cstddef>
#include <cstdint>
#include <type_traits>
#include "const_str.hpp"



template <typename T>
struct is_special{
    static constexpr bool value = false;
};

template <typename T>
inline constexpr bool is_special_v = is_special<T>::value;


// special types:

template <>
struct is_special<const char*>{
    static constexpr bool value = true;
};

// type str generation

template<typename T, bool special=is_special_v<T>, typename Enable = void>
struct type_str;

template<>
struct type_str<int8_t>{
    static constexpr const_str<2> str = "i8";
};

template<>
struct type_str<uint8_t>{
    static constexpr const_str<2> str = "u8";
};

template<>
struct type_str<int32_t>{
    static constexpr const_str<3> str = "i32";
};

template<>
struct type_str<uint32_t>{
    static constexpr const_str<3> str = "u32";
};

template<>
struct type_str<int16_t>{
    static constexpr const_str<3> str = "i16";
};

template<>
struct type_str<uint16_t>{
    static constexpr const_str<3> str = "u16";
};

template<>
struct type_str<int64_t>{
    static constexpr const_str<3> str = "i64";
};

template<>
struct type_str<uint64_t>{
    static constexpr const_str<3> str = "u64";
};

template<>
struct type_str<float>{
    static constexpr const_str<3> str = "f32";
};

template<>
struct type_str<double>{
    static constexpr const_str<3> str = "f64";
};

template<>
struct type_str<const char*>{
    static constexpr const_str<5> str = "*cstr";
};

template<>
struct type_str<void>{
    static constexpr const_str<4> str = "void";
};

template<typename T >
struct type_str<T, false, std::enable_if_t<std::is_pointer_v<T>> >{
    static constexpr auto str = make_const_str("*")+type_str<std::remove_pointer_t<T>>::str;
};


#define TYPE_ATTR_DEFINE_CLASS_NAMESTR(classname,namestr)  \
template<>                                                 \
struct type_str<classname> {                               \
    static constexpr auto str = make_const_str(namestr);   \
};

