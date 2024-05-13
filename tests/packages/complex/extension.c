// SPDX-FileCopyrightText: 2024 The meson-python developers
//
// SPDX-License-Identifier: MIT

#include <Python.h>

static PyObject* answer(PyObject* self) {
    return PyLong_FromLong(42);
}

static PyMethodDef methods[] = {
    {"answer", (PyCFunction) answer, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "extension",
    NULL,
    -1,
    methods,
};

PyMODINIT_FUNC PyInit_extension(void) {
    return PyModule_Create(&module);
}
