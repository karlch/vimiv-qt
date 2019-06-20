/*******************************************************************************
*                           C extension for vimiv
* Simple add-on to manipulate brightness and contrast of an image on the pixel
* scale.
*******************************************************************************/

#include <Python.h>
#include <stdio.h>

#include "manipulate.h"
#include "math_func_eval.h"

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

/*****************************
*  Initialize python module  *
*****************************/

static PyMethodDef ManipulateMethods[] = {
    {"manipulate", manipulate_bc, METH_VARARGS, "Manipulate brightness and contrast"},
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

/***************************************
*  Actual C functions doing the math  *
***************************************/

/* Make sure value stays between 0 and 255 */
static inline U_CHAR clamp(float value)
{
    if (value < 0)
        return 0;
    else if (value > 1)
        return 255;
    return (U_CHAR) (value * 255);
}

/* Enhance brightness using the GIMP algorithm. */
static inline float enhance_brightness(float value, float factor)
{
    if (factor < 0)
        return value * (1 + factor);
    return value + (1 - value) * factor;
}

/* Enhance contrast using the GIMP algorithm:
   value = (value - 0.5) * (tan ((factor + 1) * PI/4) ) + 0.5; */
static inline float enhance_contrast(float value, float factor)
{
    U_CHAR tan_pos = (U_CHAR) (factor * 127 + 127);
    return (value - 0.5) * (TAN[tan_pos]) + 0.5;
}

/* Return the ARGB content of one pixel at index in data. */
static inline void set_pixel_content(U_CHAR* data, int index, U_CHAR* content)
{
    for (U_SHORT i = 0; i < 4; i++)
        content[i] = data[index + i];
}

/* Read pixel data of specific size and enhance brightness and contrast
   according to the two functions above. Change the values in which
   is of type char* so one pixel is equal to one byte allowing to create a
   python memoryview obect directly from memory. */
void enhance_bc_c(U_CHAR* data, const int size, float brightness, float contrast)
{
    float value;

    for (int pixel = 0; pixel < size; pixel++) {
        /* Skip alpha channel */
        if (pixel % 4 != ALPHA_CHANNEL) {
            value = ((float) data[pixel]) / 255.;
            value = enhance_brightness(value, brightness);
            value = enhance_contrast(value, contrast);
            value = clamp(value);
            data[pixel] = value;
        }
    }
}
