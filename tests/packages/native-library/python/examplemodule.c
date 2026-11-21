// SPDX-FileCopyrightText: 2026 The meson-python developers
//
// SPDX-License-Identifier: MIT

#include <Python.h>
#include "example.h"

static PyObject *add(PyObject *self, PyObject *args) {
    int a, b;
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
    return PyLong_FromLong(example_add(a, b));
}

static PyMethodDef methods[] = {
    {"add", add, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {PyModuleDef_HEAD_INIT, "example", NULL, -1, methods};

PyMODINIT_FUNC PyInit_example(void) {
    return PyModule_Create(&module);
}
