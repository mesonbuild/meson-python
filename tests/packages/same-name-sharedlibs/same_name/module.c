// SPDX-FileCopyrightText: 2026 The meson-python developers
//
// SPDX-License-Identifier: MIT

#include <Python.h>

extern int choice(void);

static PyObject *value(PyObject *self, PyObject *args) {
    return PyLong_FromLong(choice());
}

static PyMethodDef methods[] = {
    {"value", value, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT, "choice", NULL, -1, methods,
};

PyMODINIT_FUNC PyInit_choice(void) {
    return PyModule_Create(&module);
}
