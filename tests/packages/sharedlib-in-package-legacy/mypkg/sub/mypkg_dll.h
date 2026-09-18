// SPDX-FileCopyrightText: 2022 The meson-python developers
//
// SPDX-License-Identifier: MIT

#pragma once

// MYPKG_DLL
// inspired by https://github.com/abseil/abseil-cpp/blob/20240116.2/absl/base/config.h#L736-L753
// and https://github.com/scipy/scipy/blob/9ded83b51099eee745418ccbb30196db96c81f3f/scipy/_build_utils/src/scipy_dll.h
//
// When building the `examplelib` DLL, this macro expands to `__declspec(dllexport)`
// so we can annotate symbols appropriately as being exported. When used in
// headers consuming a DLL, this macro expands to `__declspec(dllimport)` so
// that consumers know the symbol is defined inside the DLL. In all other cases,
// the macro expands to nothing.
// Note: MYPKG_DLL_{EX,IM}PORTS are set in mypkg/meson.build
#if defined(MYPKG_DLL_EXPORTS)
    #define MYPKG_DLL __declspec(dllexport)
#elif defined(MYPKG_DLL_IMPORTS)
    #define MYPKG_DLL __declspec(dllimport)
#else
    #define MYPKG_DLL
#endif
