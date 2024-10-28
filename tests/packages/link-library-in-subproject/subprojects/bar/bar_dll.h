// SPDX-FileCopyrightText: 2024 The meson-python developers
//
// SPDX-License-Identifier: MIT

#pragma once

// When building the `examplelib` DLL, this macro expands to `__declspec(dllexport)`
// so we can annotate symbols appropriately as being exported. When used in
// headers consuming a DLL, this macro expands to `__declspec(dllimport)` so
// that consumers know the symbol is defined inside the DLL. In all other cases,
// the macro expands to nothing.
// Note: BAR_DLL_{EX,IM}PORTS are set in meson.build
#if defined(BAR_DLL_EXPORTS)
    #define BAR_DLL __declspec(dllexport)
#elif defined(BAR_DLL_IMPORTS)
    #define BAR_DLL __declspec(dllimport)
#else
    #define BAR_DLL
#endif
