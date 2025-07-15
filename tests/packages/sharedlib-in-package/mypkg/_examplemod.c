// SPDX-FileCopyrightText: 2022 The meson-python developers
//
// SPDX-License-Identifier: MIT

#include <Python.h>

#include "lib.h"

static PyObject* example_prodsum(PyObject* self, PyObject *args)
{
    int a, b, x;

    if (!PyArg_ParseTuple(args, "iii", &a, &b, &x)) {
        return NULL;
    }

    long result = prodsum(a, b, x);

    return PyLong_FromLong(result);
}

static PyMethodDef methods[] = {
    {"prodsum", (PyCFunction)example_prodsum, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_example",
    NULL,
    -1,
    methods,
};

PyMODINIT_FUNC PyInit__example(void)
{
    return PyModule_Create(&module);
}
