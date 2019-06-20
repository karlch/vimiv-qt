/*******************************************************************************
*                           C extension for vimiv
* definitions usable for more modules.
*******************************************************************************/
#ifndef definitions_h__
#define definitions_h__

/*****************************************
*  Alpha channel depends on endianness  *
*****************************************/
#if G_BYTE_ORDER == G_LITTLE_ENDIAN /* BGRA */

#define ALPHA_CHANNEL 3
#define R_CHANNEL 2
#define G_CHANNEL 1
#define B_CHANNEL 0

#elif G_BYTE_ORDER == G_BIG_ENDIAN /* ARGB */

#define ALPHA_CHANNEL 0
#define R_CHANNEL 1
#define G_CHANNEL 2
#define B_CHANNEL 3

#else /* PDP endianness: RABG */

#define ALPHA_CHANNEL 1
#define R_CHANNEL 0
#define G_CHANNEL 2
#define B_CHANNEL 3

#endif

/*************
*  Typedefs  *
*************/
typedef unsigned short U_SHORT;
typedef unsigned char U_CHAR;

#endif  // ifndef definitions_h__
