/*******************************************************************************
*                           C extension for vimiv
* Simple add-on to manipulate brightness and contrast of an image on the pixel
* scale.
*******************************************************************************/

#include <Python.h>
#include <stdio.h>

#include "brightness_contrast.h"
#include "hue_saturation_lightness.h"

/*****************************
*  Generate python functions *
*****************************/

static PyObject *
manipulate_bc(PyObject *self, PyObject *args)
{
    /* Receive arguments from python */
    PyObject *py_data;
    float brightness;
    float contrast;
    if (!PyArg_ParseTuple(args, "Off",
                          &py_data, &brightness, &contrast))
        return NULL;

    /* Convert python bytes to U_CHAR* for pixel data */
    if (!PyBytes_Check(py_data)) {
        PyErr_SetString(PyExc_TypeError, "Expected bytes");
        return NULL;
    }
    U_CHAR* data = (U_CHAR*) PyBytes_AsString(py_data);
    const int size = PyBytes_Size(py_data);

    /* Run the C function to enhance brightness and contrast */
    enhance_bc_c(data, size, brightness, contrast);

    /* Return python bytes of updated data */
    return PyBytes_FromStringAndSize((char*) data, size);
}

static PyObject *
manipulate_hsl(PyObject *self, PyObject *args)
{
    /* Receive arguments from python */
    PyObject *py_data;
    float hue;
    float saturation;
    float lightness;
    if (!PyArg_ParseTuple(args, "Offf",
                          &py_data, &hue, &saturation, &lightness))
        return NULL;

    /* Convert python bytes to U_CHAR* for pixel data */
    if (!PyBytes_Check(py_data)) {
        PyErr_SetString(PyExc_TypeError, "Expected bytes");
        return NULL;
    }
    U_CHAR* data = (U_CHAR*) PyBytes_AsString(py_data);
    const int size = PyBytes_Size(py_data);

    /* Run the C function to enhance brightness and contrast */
    enhance_hsl_c(data, size, hue, saturation, lightness);

    /* Return python bytes of updated data */
    return PyBytes_FromStringAndSize((char*) data, size);
}

/*****************************
*  Initialize python module  *
*****************************/

static PyMethodDef ManipulateMethods[] = {
    {"brightness_contrast", manipulate_bc, METH_VARARGS, "Manipulate brightness and contrast"},
    {"hue_saturation_lightness", manipulate_hsl, METH_VARARGS, "Manipulate hue, saturation and lightness"},
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

static struct PyModuleDef manipulate = {
    PyModuleDef_HEAD_INIT,
    "_c_manipulate", /* Name */
    NULL,                /* Documentation */
    -1,                  /* Keep state in global variables */
    ManipulateMethods
};

PyMODINIT_FUNC
PyInit__c_manipulate(void)
{
    PyObject *m = PyModule_Create(&manipulate);
    if (m == NULL)
        return NULL;
    return m;
}
