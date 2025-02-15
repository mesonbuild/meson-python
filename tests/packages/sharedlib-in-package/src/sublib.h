// SPDX-FileCopyrightText: 2022 The meson-python developers
//
// SPDX-License-Identifier: MIT

#if defined(MYPKG_DLL_EXPORTS)
    #define EXPORT __declspec(dllexport)
#elif defined(MYPKG_DLL_IMPORTS)
    #define EXPORT __declspec(dllimport)
#else
    #define EXPORT
#endif

EXPORT int prod(int a, int b);
