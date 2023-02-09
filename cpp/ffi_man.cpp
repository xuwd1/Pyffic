#include "ffi_man.hpp"

FFIAccessEntry FFIAccessEntry::make_global_func_entry(void* ptr, const char* func_name, const char* func_sig_str){
    FFIAccessEntry ret;
    ret.type = FFIAccessEntryType::kGlobalFunc;
    ret.ptr = ptr;
    ret.name = func_name;
    ret.sig = func_sig_str;
    return ret;
}
FFIAccessEntry FFIAccessEntry::make_class_method_entry(void* ptr, const char* method_name, const char* method_sig_str){
    FFIAccessEntry ret;
    ret.type = FFIAccessEntryType::kClassMethod;
    ret.ptr = ptr;
    ret.name = method_name;
    ret.sig = method_sig_str;
    return ret;
}
FFIAccessEntry FFIAccessEntry::make_class_field_entry(const char* register_name, const char* field_sig_str, size_t offset, size_t field_size){
    FFIAccessEntry ret;
    ret.type = FFIAccessEntryType::kClassField;
    ret.name = register_name;
    ret.sig = field_sig_str;
    ret.offset = offset;
    ret.field_size = field_size;
    return ret;
}

FFIClassEntry FFIClassEntry::make_class_entry(const char* class_namestr,
                                      void* construct_func_ptr,
                                      const char* construct_func_sig,
                                      void* destroy_func_ptr,
                                      const char* destroy_func_sig)
{
    FFIClassEntry ret{
        .class_namestr = class_namestr,
        .construct_func_ptr = construct_func_ptr,
        .construct_func_sig = construct_func_sig,
        .destroy_func_ptr = destroy_func_ptr,
        .destroy_func_sig = destroy_func_sig
    };
    return ret;
}

int check_accessentry(const FFIAccessEntry& entry){
    // TODO: custom checking here
    return 0;
}
int check_classentry(const FFIClassEntry& entry){
    // TODO: custom checking here
    return 0;
}


extern "C"{
    FFIManager* ffi_get_manager_instance(){
        return FFIManager::getInstance();
    }
    uint64_t ffi_get_class_entry_num(){
        return FFIManager::getInstance()->class_entry_num();
    }
    uint64_t ffi_get_access_entry_num(){
        return FFIManager::getInstance()->access_entry_num();
    }
    FFIClassEntry* ffi_get_class_entry(uint64_t index){
        return &FFIManager::getInstance()->get_class_entry(index);
    }
    FFIAccessEntry* ffi_get_access_entry(uint64_t index){
        return &FFIManager::getInstance()->get_access_entry(index);
    }
    void ffi_print_all_entries(){
        FFIManager::getInstance()->_print_access_entries();
        FFIManager::getInstance()->_print_class_entries();
    }
}