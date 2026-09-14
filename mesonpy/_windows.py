import ctypes
from ctypes import wintypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

IsWow64Process2 = kernel32.IsWow64Process2
IsWow64Process2.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(wintypes.USHORT),
    ctypes.POINTER(wintypes.USHORT),
]
IsWow64Process2.restype = wintypes.BOOL

IMAGE_FILE_MACHINE_UNKNOWN = 0x0000
IMAGE_FILE_MACHINE_AMD64   = 0x8664
IMAGE_FILE_MACHINE_ARM64   = 0xAA64
IMAGE_FILE_MACHINE_I386    = 0x014c

MACHINE = {
    IMAGE_FILE_MACHINE_UNKNOWN: 'unknown', # native, no WOW64
    IMAGE_FILE_MACHINE_AMD64: 'amd64',
    IMAGE_FILE_MACHINE_ARM64: 'arm64',
    IMAGE_FILE_MACHINE_I386: 'x86',
}

def platform():
    handle = kernel32.GetCurrentProcess()

    process = wintypes.USHORT()
    native = wintypes.USHORT()
    
    r = IsWow64Process2(handle, ctypes.byref(process), ctypes.byref(native))
    if not r:    
        raise ctypes.WinError(ctypes.get_last_error())
    
    return native.value, process.value, MACHINE[native.value], MACHINE[process.value]
