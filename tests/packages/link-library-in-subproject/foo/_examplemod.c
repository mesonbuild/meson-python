// SPDX-FileCopyrightText: 2022 The meson-python developers
//
// SPDX-License-Identifier: MIT

#include <Python.h>

#include "examplelib.h"

static PyObject* example_sum(PyObject* self, PyObject *args)
{
    int a, b;
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }

    long result = sum(a, b);

    return PyLong_FromLong(result);
}

static PyMethodDef methods[] = {
    {"example_sum", (PyCFunction)example_sum, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL},
};

#if PY_VERSION_HEX >= 0x030F0000
/* Use `PyModExport_<modname>` hook, new in Python 3.15 (PEP 793) */
static PyModuleDef_Slot example_slots[] = {
    {Py_mod_name, "_example"},
    {Py_mod_methods, methods},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, NULL}
};

PyMODEXPORT_FUNC
PyModExport__example(void)
{
    return example_slots;
}
#else
/* Use legacy method to create a module dynamically */
static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_example",
    NULL,
    -1,
    methods,
};

PyMODINIT_FUNC PyInit__example(void)
{
    PyObject *module;

    module = PyModule_Create(&moduledef);
    if (module == NULL) {
        return module;
    }

#if Py_GIL_DISABLED
    PyUnstable_Module_SetGIL(module, Py_MOD_GIL_NOT_USED);
#endif

    return module;
}
#endif
