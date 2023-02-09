from enum import Enum

class FFIAccessEntryType(Enum):
    kGlobalFunc = 1
    kClassMethod = 2
    kClassField = 3  