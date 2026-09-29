// SPDX-FileCopyrightText: 2026 The meson-python developers
//
// SPDX-License-Identifier: MIT

#include <Python.h>
#include <geos_c.h>

static PyObject *version(PyObject *self, PyObject *args) {
    return PyUnicode_FromString(GEOSversion());
}

static PyMethodDef methods[] = {
    {"version", version, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT, "external", NULL, -1, methods,
};

PyMODINIT_FUNC PyInit_external(void) {
    return PyModule_Create(&module);
}
