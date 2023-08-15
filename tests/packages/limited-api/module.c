// SPDX-FileCopyrightText: 2023 The meson-python developers
//
// SPDX-License-Identifier: MIT

#include <Python.h>

static PyObject* add(PyObject *self, PyObject *args) {
    int a, b;

    if (!PyArg_ParseTuple(args, "ii", &a, &b))
        return NULL;

    return PyLong_FromLong(a + b);
}

static PyMethodDef methods[] = {
    {"add", add, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "plat",
    NULL,
    -1,
    methods,
};

PyMODINIT_FUNC PyInit_module(void) {
    return PyModule_Create(&module);
}
