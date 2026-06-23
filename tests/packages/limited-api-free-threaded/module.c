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

PyABIInfo_VAR(abi_info);

static PySlot module_slots[] = {
    PySlot_STATIC_DATA(Py_mod_name, "module"),
    PySlot_STATIC_DATA(Py_mod_methods, methods),
    PySlot_DATA(Py_mod_gil, Py_MOD_GIL_NOT_USED),
    PySlot_DATA(Py_mod_abi, &abi_info),
    PySlot_END,
};

PyMODEXPORT_FUNC PyModExport_module(void) {
    return module_slots;
}
