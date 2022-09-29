// This example is adapted from the spam example taken from the python documentation
// and is available here: https://docs.python.org/3/extending/extending.html
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *SpamError;

// Define a method that will be part of the module. This method
// passes the arguments to `system()` and returns the output.
static PyObject * spam_system(PyObject *self, PyObject *args) {
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command)) return NULL;
    sts = system(command);
    return PyLong_FromLong(sts);
}

// Methods table containing the methods exposed to the python interpreter
static PyMethodDef SpamMethods[] = {
    {"system",  spam_system, METH_VARARGS, "Execute a shell command."},
    {NULL, NULL, 0, NULL}               // Sentinel value
};

static struct PyModuleDef spammodule = {
    PyModuleDef_HEAD_INIT,
    "spam",                             // name of module
    "An example C extension to python", // module documentation, may be NULL
    -1,                                 // size of per-interpreter state of the module, or -1 if the
                                        // module keeps state in global variables.
    SpamMethods
};

// The initialization function must be named PyInit_<name>(), where <name> is the name of the module,
// and should be the only non-static item defined in the module file.
PyMODINIT_FUNC PyInit__spam(void) {
    PyObject *m;

    m = PyModule_Create(&spammodule);
    if (m == NULL) return NULL;

    SpamError = PyErr_NewException("spam.error", NULL, NULL);
    Py_XINCREF(SpamError);
    if (PyModule_AddObject(m, "error", SpamError) < 0) {
        Py_XDECREF(SpamError);
        Py_CLEAR(SpamError);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}

// When embedding Python, the PyInit_spam() function is not called automatically unless there’s an
// entry in the PyImport_Inittab table. To add the module to the initialization table, use
// PyImport_AppendInittab().
int main(int argc, char *argv[]) {

    // RFC: according to https://docs.python.org/3/c-api/sys.html#c.Py_DecodeLocale, this function
    // should not be called before Py_PreInitialize(). Normally I'd expect that this would be fine
    // if you're importing this function from the REPL, because at that point I think
    // Py_PreInitialize() has been called.
    wchar_t *program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        exit(1);
    }

    // Add a built-in module, before Py_Initialize
    if (PyImport_AppendInittab("spam", PyInit__spam) == -1) {
        fprintf(stderr, "Error: could not extend in-built modules table\n");
        exit(1);
    }

    // Pass argv[0] to the Python interpreter.
    Py_SetProgramName(program);

    // Initialize the Python interpreter. Required. If this step fails, it will be a fatal error.
    Py_Initialize();

    PyMem_RawFree(program);
    return 0;
}
