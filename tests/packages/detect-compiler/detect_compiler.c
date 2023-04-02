// SPDX-FileCopyrightText: 2023 The meson-python developers
//
// SPDX-License-Identifier: MIT

#include <Python.h>

#if defined _MSC_VER
#  define _COMPILER "msvc"
#elif defined __clang__
#  define _COMPILER "clang"
#elif defined __GNUC__
#  define _COMPILER "gcc"
#else
#  define _COMPILER "unknown"
#endif

static PyObject* compiler(PyObject* self)
{
    return PyUnicode_FromString(_COMPILER);
}

static PyMethodDef methods[] = {
    {"compiler", (PyCFunction)compiler, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "detect_compiler",
    NULL,
    -1,
    methods,
};

PyMODINIT_FUNC PyInit_detect_compiler(void)
{
    return PyModule_Create(&module);
}
