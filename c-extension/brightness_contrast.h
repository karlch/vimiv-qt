/*******************************************************************************
*                           C extension for vimiv
* Functions to enhance brightness and contrast of an image.
*******************************************************************************/

#include "definitions.h"
#include "helper_func.h"
#include "math_func_eval.h"

/**
 * Enhance brightness using the GIMP algorithm.
 *
 * @param value Current R/G/B value of the pixel.
 * @param factor Factor to enhance brightness by.
 */
static inline float enhance_brightness(float value, float factor)
{
    if (factor < 0)
        return value * (1 + factor);
    return value + (1 - value) * factor;
}

/**
 * Enhance contrast using the GIMP algorithm:
 *
 * value = (value - 0.5) * (tan ((factor + 1) * PI/4) ) + 0.5
 *
 * @param value Current R/G/B value of the pixel.
 * @param factor Factor to enhance contrast by.
 */
static inline float enhance_contrast(float value, float factor)
{
    U_CHAR tan_pos = (U_CHAR) (factor * 127 + 127);
    return (value - 0.5) * (TAN[tan_pos]) + 0.5;
}

/**
 * Enhance brightness and contrast of an image.
 *
 * @param data Image pixel data to update.
 * @param size Total size of the data.
 * @param brightness Factor to enhance brightness by.
 * @param contrast Factor to enhance contrast by.
 */
static void enhance_bc_c(U_CHAR* data, const int size, float brightness, float contrast)
{
    float value;

    for (int pixel = 0; pixel < size; pixel++) {
        /* Skip alpha channel */
        if (pixel % 4 != ALPHA_CHANNEL) {
            value = ((float) data[pixel]) / 255.;
            value = enhance_brightness(value, brightness);
            value = enhance_contrast(value, contrast);
            value = pixel_value(value);
            data[pixel] = value;
        }
    }
}
