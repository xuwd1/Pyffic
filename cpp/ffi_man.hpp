#pragma once
#include <cstdint>
#include <cstddef>
#include <type_traits>
#include <vector>
#include <cstdio>
#include <mutex>
#include "siggen/sig_gen.hpp"
#include "siggen/mf_helper.hpp"

enum class FFIAccessEntryType:int32_t{
    kGlobalFunc = 1,
    kClassMethod = 2,
    kClassField = 3  
};

/*
    FFIAccessEntry entry
    when type is kGlobalFunc:
        - ptr: function pointer
        - name: registered function name
        - sig: generated function signature string
        - offset : NA
        - field_size : NA (or maybe pointer type size?)
    when type is kClassMethod:
        - ptr: function pointer
        - name: registered method name, must be in format Classname.methodname
        - sig: generated function signature string
        - offset : NA
        - field_size : NA (or maybe pointer type size?)
    when type is kClassField:
        - ptr: NA
        - name: register name
        - sig: generated field type string
        - offset : offset to the class pointer
        - field_size : field size in bytes
*/
struct FFIAccessEntry{
    FFIAccessEntryType type;
    void* ptr;
    const char* name;
    const char* sig;

    // only for classfield
    size_t offset;
    size_t field_size;
    static FFIAccessEntry make_global_func_entry(void* ptr, const char* func_name, const char* func_sig_str);
    static FFIAccessEntry make_class_method_entry(void* ptr, const char* method_name, const char* method_sig_str);
    static FFIAccessEntry make_class_field_entry(const char* register_name, const char* field_sig_str, size_t offset, size_t field_size);
};
//POD CHECK 
static_assert(std::is_trivial_v<FFIAccessEntry>,"");
static_assert(std::is_standard_layout_v<FFIAccessEntry>,"");

int check_accessentry(const FFIAccessEntry& entry);

struct FFIClassEntry{
    const char* class_namestr;
    void* construct_func_ptr;
    const char* construct_func_sig;
    void* destroy_func_ptr;
    const char* destroy_func_sig;
    static FFIClassEntry make_class_entry(const char* class_namestr,
                                          void* construct_func_ptr,
                                          const char* construct_func_sig,
                                          void* destroy_func_ptr,
                                          const char* destroy_func_sig);
};
//POD CHECK 
static_assert(std::is_trivial_v<FFIClassEntry>,"");
static_assert(std::is_standard_layout_v<FFIClassEntry>,"");

int check_classsentry(const FFIAccessEntry& entry);

class FFIManager
{
public:
    static FFIManager* getInstance(){
        static FFIManager instance;
        return &instance;
    }
    FFIAccessEntry& add_access_entry(FFIAccessEntry new_entry){
        lock.lock();
        access_entries.push_back(new_entry);
        auto& ret = access_entries.back();
        lock.unlock();
        return ret;
    }
    uint64_t access_entry_num(){
        lock.lock();
        auto ret = access_entries.size();
        lock.unlock();
        return ret;
    }
    FFIAccessEntry& get_access_entry(size_t index){
        return access_entries[index];
    }
    FFIClassEntry& add_class_entry(FFIClassEntry new_entry){
        lock.lock();
        class_entries.push_back(new_entry);
        auto& ret = class_entries.back();
        lock.unlock();
        return ret;
    }
    uint64_t class_entry_num(){
        lock.lock();
        auto ret = class_entries.size();
        lock.unlock();
        return ret;
    }
    FFIClassEntry& get_class_entry(size_t index){
        return class_entries[index];
    }

    void _print_access_entries(){
        for (auto& v: access_entries){
            if (v.type == FFIAccessEntryType::kClassField){
                printf("[CF]%s: type: %s, offset:%ld, size:%ld\n",v.name,v.sig,v.offset,v.field_size);
            } 
            if (v.type == FFIAccessEntryType::kGlobalFunc){
                printf("[GF]%s: addr: %p, sig: <%s>\n",v.name,v.ptr,v.sig);
            }
            if (v.type == FFIAccessEntryType::kClassMethod){
                printf("[CM]%s: addr: %p, sig: <%s>\n",v.name,v.ptr,v.sig);
            }
            
        }
    }
    void _print_class_entries(){
        for (auto& v: class_entries){
            printf("[CLS]%s: constructor: %p, <%s>, destructor: %p, <%s>\n",v.class_namestr,v.construct_func_ptr,v.construct_func_sig,v.destroy_func_ptr,v.destroy_func_sig);
        }
    }
    
private:
    //private constructor
    //insane technique!
    FFIManager(){
    }   
    bool initialized;
    std::vector<FFIAccessEntry> access_entries;
    std::vector<FFIClassEntry> class_entries;
    std::mutex lock;
    
public:
    // delete cp
    FFIManager(const FFIManager& other) = delete;
    // delete cp-asmt 
    void operator=(const FFIManager& other) = delete;
};

extern "C"{
    FFIManager* ffi_get_manager_instance();
    uint64_t ffi_get_class_entry_num();
    uint64_t ffi_get_access_entry_num();
    FFIClassEntry* ffi_get_class_entry(uint64_t index);
    FFIAccessEntry* ffi_get_access_entry(uint64_t index);
    void ffi_print_all_entries();
}




// helper macros

#define merge_body(x,y) x ## y
#define merge(x,y) merge_body(x,y)

#define FFI_REGISTER_GLOBAL_FUNCTION(func,register_name) \
auto merge(_ffi_access_entry_, __COUNTER__)   \
=FFIManager::getInstance()->add_access_entry( \
FFIAccessEntry::make_global_func_entry( \
reinterpret_cast<void*>(&func),register_name,signature<decltype(func)>::sig.c_str() \
));

// use __COUNTER__ to generate different mf_wrapper type to wrap memberfunctions having same type
#define FFI_REGISTER_CLASS_METHOD(func,register_name) \
auto merge(_ffi_access_entry_, __COUNTER__) \
=FFIManager::getInstance()->add_access_entry(   \
FFIAccessEntry::make_class_method_entry( \
reinterpret_cast<void*>(&make_mf_wrapper<__COUNTER__>(func).wrapper_function) ,\
register_name ,\
signature<wrapped_memf_type<decltype(func)>::type>::sig.c_str() \
));


#define FFI_REGISTER_CLASS_FIELD(cls,field,combine,register_name) \
auto merge(_ffi_access_entry_, __COUNTER__) \
=FFIManager::getInstance()->add_access_entry(   \
FFIAccessEntry::make_class_field_entry( \
register_name, \
type_str<decltype(combine)>::str.c_str(), \
offsetof(cls,field), \
sizeof(combine)));

#define FFI_REGISTER_CLASS(class,registername,construct_func,destroy_func) \
TYPE_ATTR_DEFINE_CLASS_NAMESTR(class, registername); \
auto merge(_ffi_class_entry_, __COUNTER__) \
=FFIManager::getInstance()->add_class_entry( \
FFIClassEntry::make_class_entry( \
registername, \
reinterpret_cast<void*>(construct_func),  \
signature<decltype(construct_func)>::sig.c_str(), \
reinterpret_cast<void*>(destroy_func), \
signature<decltype(destroy_func)>::sig.c_str() \
));  