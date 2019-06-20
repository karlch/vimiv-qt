/*******************************************************************************
*                           C extension for vimiv
* Small inline helper functions
*******************************************************************************/
#ifndef helper_func_h__
#define helper_func_h__

#include "definitions.h"

/**
 * Return the minimum of two numbers.
 */
inline float min2(float a, float b) {
    return a < b ? a : b;
}

/**
 * Return the maximum of two numbers.
 */
inline float max2(float a, float b) {
    return a > b ? a : b;
}

/**
 * Return the minimum of three numbers.
 */
inline float min3(float a, float b, float c) {
    if (a <= b && a <= c)
        return a;
    else if (b <= c)
        return b;
    return c;
}

/**
 * Return the maximum of three numbers.
 */
inline float max3(float a, float b, float c) {
    if (a >= b && a >= c)
        return a;
    else if (b >= c)
        return b;
    return c;
}

/**
 * Ensure a number stays within lower and upper.
 */
inline float clamp(float value, float lower, float upper) {
    if (value < lower)
        return lower;
    if (value > upper)
        return upper;
    return value;
}

/**
 * Return the remainder of a floating point division.
 */
inline float remainder_fl(float dividend, float divisor) {
    int intdiv = dividend / divisor;
    return dividend - intdiv * divisor;
}

/**
 * Return a valid pixel value (0..255) from a floating point value (0..1).
 */
static inline U_CHAR pixel_value(float value) {
    return (U_CHAR) clamp(value * 255, 0, 255);
}

#endif  // ifndef helper_func_h__
