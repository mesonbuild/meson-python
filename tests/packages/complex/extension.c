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
    PyObject *m = PyModule_Create(&module);
    if (m == NULL) {
        return NULL;
    }
#ifdef Py_GIL_DISABLED
    PyUnstable_Module_SetGIL(m, Py_MOD_GIL_NOT_USED);
#endif
    return m;
}
