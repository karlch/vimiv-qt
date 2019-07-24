/*******************************************************************************
*                           C extension for vimiv
* Functions to enhance hue, saturation and value of an image.
*******************************************************************************/

#include "definitions.h"
#include "helper_func.h"

/**
 * Enhance hue using the GIMP algorithm.
 *
 * @param hue Initial hue to enhance.
 * @param v Value to change hue by.
 */
inline float enhance_hue(float hue, float v) {
    hue += v;
    if (hue > 360)
        return hue - 360;
    if (hue < 0)
        return hue + 360;
    return hue;
}

/**
 * Enhance saturation using the GIMP algorithm.
 *
 * @param saturation Initial saturation to enhance.
 * @param v Value to change saturation by.
 */
inline float enhance_saturation(float saturation, float v) {
    saturation *= (v + 1);
    return clamp(saturation, 0, 1);
}

/**
 * Enhance lightness using the GIMP algorithm
 *
 * @param lightness Initial lightness to enhance.
 * @param v Value to change lightness by.
 */
inline float enhance_lightness(float lightness, float v) {
    if (v < 0)
        return lightness * (v + 1.0);
    return lightness + (v * (1.0 - lightness));
}

/**
 * Convert RGB to HSL.
 *
 * See https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
 */
static void rgb_to_hsl(float r, float g, float b, float* h, float* s, float* l) {
    float MIN = min3(r, g, b);
    float MAX = max3(r, g, b);

    // Hue
    if (MIN == MAX)
        *h = 0;
    else if (MAX == r)
        *h = 60 * (g - b) / (MAX - MIN);
    else if (MAX == g)
        *h = 60 * (2 + (b - r) / (MAX - MIN));
    else
        *h = 60 * (4 + (r - g) / (MAX - MIN));
    *h = *h < 0 ? *h + 360 : *h;

    // Lightness
    *l = (MAX + MIN) / 2.;

    // Saturation
    if (MAX == 0 || MIN == 1)
        *s = 0;
    else
        *s = (MAX - *l) / min2(*l, 1 - *l);
}

/**
 * Helper function to convert HSL to RGB.
 */
inline float hsl_to_rgb_helper(float a, float n, float h, float l) {
    float k = remainder_fl((n + h / 30.), 12.);
    return l - a * max2(min3(k - 3, 9 - k, 1), -1);
}

/**
 * Convert HSL to RGB.
 *
 * See https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB.
 */
static void hsl_to_rgb(float h, float s, float l, float* r, float* g, float* b) {
    float a =  s * min2(l, 1 - l);

    *r = hsl_to_rgb_helper(a, 0, h, l);
    *g = hsl_to_rgb_helper(a, 8, h, l);
    *b = hsl_to_rgb_helper(a, 4, h, l);
}

/**
 * Enhance hue, saturation and lightness of an image.
 *
 * This requires converting the image data to the HSL space, applying changes there and then
 * converting back to RGB.
 *
 * @param data Image pixel data to update.
 * @param size Total size of the data.
 * @param hue Value to change hue by.
 * @param saturation Value to change saturation by.
 * @param lightness Value to change lightness by.
 */
static void enhance_hsl_c(U_CHAR* data, const int size, float hue, float saturation,
                   float lightness)
{
    float r, g, b, h, s, l;

    int channels = 4; // RGBA channels

    for (int pixel = 0; pixel < size; pixel += channels) {
        r = ((float) data[pixel + R_CHANNEL]) / 255.;
        g = ((float) data[pixel + G_CHANNEL]) / 255.;
        b = ((float) data[pixel + B_CHANNEL]) / 255.;
        rgb_to_hsl(r, g, b, &h, &s, &l);
        hsl_to_rgb(
            enhance_hue(h, hue),
            enhance_saturation(s, saturation),
            enhance_lightness(l, lightness),
            &r, &g, &b
        );
        data[pixel + R_CHANNEL] = pixel_value(r);
        data[pixel + G_CHANNEL] = pixel_value(g);
        data[pixel + B_CHANNEL] = pixel_value(b);
    }
}
