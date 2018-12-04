/* Sizes of ingteral types. */

/*
 *  Note: Negative values are parenthesized to ensure macro safety. The parens
 *  may be able to be removed if it can be proven that no such issues are
 *  possible.
 */

/* Maximum number of bits for smallest object that is not a bit-field (byte). */
#define CHAR_BIT 8

/* Minimum value for an object of type signed char. */
#define SCHAR_MIN (-128)

/* Maximum value for an object of type signed char. */
#define SCHAR_MAX 127

/* Maximum value for an object of type unsigned char. */
#define UCHAR_MAX 255

/* Minimum value for an object of type char. */
#define CHAR_MIN 0

/* Maximum value for an object of type char. */
#define CHAR_MAX UCHAR_MAX

/* Maximum number of bytes in a multibyte character, for any supported locale. */
#define MB_LEN_MAX 1

/* Minimum value for an object of type short int. */
#define SHRT_MIN (-32768)

/* Maximum value for an object of type short int. */
#define SHRT_MAX 32767

/* Maximum value for an object of type unsigned short int. */
#define USHRT_MAX 65535u

/* Minimum value for an object of type int. */
#define INT_MIN (-32767)

/* Maximum value for an object of type int. */
#define INT_MAX 32767

/* Maximum value for an object of type unsigned int. */
#define UINT_MAX 65535u

/* Minimum value for an object of type long int. */
#define LONG_MIN (-2147483648l)

/* Maximum value for an object of type long int. */
#define LONG_MAX 2147483647l

/* Maximum value for an object of type unsigned long int. */
#define ULONG_MAX 4294967295ul