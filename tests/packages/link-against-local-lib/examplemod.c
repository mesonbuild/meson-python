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

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "example",
    NULL,
    -1,
    methods,
};

PyMODINIT_FUNC PyInit_example(void)
{
    return PyModule_Create(&module);
}
