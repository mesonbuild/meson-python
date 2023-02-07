// SPDX-FileCopyrightText: 2022 The meson-python developers
//
// SPDX-License-Identifier: MIT

#include <Python.h>

static PyObject* data(PyObject* self)
{
    return PyUnicode_FromString("ABC");
}

static PyMethodDef methods[] = {
    {"data", (PyCFunction)data, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "plat",
    NULL,
    -1,
    methods,
};

PyMODINIT_FUNC PyInit_plat(void)
{
    return PyModule_Create(&module);
}
