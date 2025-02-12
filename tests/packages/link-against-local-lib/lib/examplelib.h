// SPDX-FileCopyrightText: 2022 The meson-python developers
//
// SPDX-License-Identifier: MIT

#pragma once

#if defined(EXAMPLE_DLL_EXPORTS)
    #define EXAMPLE_DLL __declspec(dllexport)
#elif defined(BAR_DLL_IMPORTS)
    #define EXAMPLE_DLL __declspec(dllimport)
#else
    #define EXAMPLE_DLL
#endif


EXAMPLE_DLL int sum(int a, int b);
