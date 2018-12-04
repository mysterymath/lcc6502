/* Characteristics of floating types. */

/*
 * These values were pulled straight from the C89 draft standard as being
 * compatible with IEEE 754 single and bouble precision.
 */

/* Rounding mode for floating-point addition (1 = To Nearest).*/
#define FLT_ROUNDS 1 

/* 
 * The following parameters define a model for a floating point type:
 * s - sign (1 or -1)
 * h - base or radix of exponent representation (an integer > 1)
 * e - exponent (an integer between a minimum e_min and a maximum e_max)
 * p - precision (the number of base-b digits in the significand)
 * f_k - nonnegative integers less than b (the significand digits) 
 * 
 *  A normalized floating-point number x (f_1 > 0 if x != 0) is defined by the following model:
 *  x = s * b^e * sum_(k=1)^p (f_k * b^(-k))
 */

/* Radix of exponent representation, b. */
#define FLT_RADIX 2

/* number of base-FLT_RADIX digits in the floating-point significand, p  */
#define FLT_MANT_DIG 24
#define DBL_MANT_DIG 53

/*
 * Number of decimal digits, q, such that any floating-point number with q
 * decimal digits can be rounded into a floating-point number and back again
 * without change to the q decimal digits. 
 * floor((p-1) * log_10 b)) + (b is a * power of 10) ? 1 : 0
 */
#define FLT_DIG 6
#define DBL_DIG 15
#define LDBL_DIG DBL_DIG

/*
 * Minimum negative integer such that FLT_RADIX raised to that
 * power minus 1 is a normalized floating-point number. e_min.
 */
#define FLT_MIN_EXP (-125)
#define DBL_MIN_EXP (-1021)
#define LDBL_MIN_EXP DBL_MIN_EXP

/*
 * Minimum negative integer such that IO raised to that power is in the range of
 * normalized floating-point numbers. ceil(log_10 b^(e_min - 1))
 */
#define FLT_MIN_10_EXP (-37)
#define DBL_MIN_10_EXP (-307)
#define LDBL_MIN_10_EXP DBL_MIN_10_EXP

/*
 * Maximum integer such that FLT_RADIX raised to that power minus 1 is a
 * representable finite floating-point number. e_max.
 */
#define FLT_MAX_EXP 128
#define DBL_MAX_EXP 1024
#define LDBL_MAX_EXP DBL_MAX_EXP

/*
 * Maximum integer such that 10 raised to that power is in the range of
 * representable finite floating-point numbers.
 * floor(log_10((1 - b^(-p)) * b^e_max))
 */
#define FLT_MAX_10_EXP 38
#define DBL_MAX_10_EXP 308
#define LDBL_MAX_10_EXP DBL_MAX_10_EXP

/*
 * Maximum representable finite floating-point number. (1 - b^(-p)) * b^e_max
 */
#define FLT_MAX (3.40282347e+38f)
#define DBL_MAX (1.7976931348623157e+308)
#define LDBL_MAX DBL_MAX

/*
 * The difference between 1 and the least value greater than 1 that is
 * representable in the given floating point type. b^(1-p)
 */
#define FLT_EPSILON (1.19209290e-07f)
#define DBL_EPSILON (2.2204460492503131e-16)
#define LDBL_EPSILON DBL_EPSILON

/*
 * Minimum normalized positive floating-point number. b^(e_min - 1)
 */
#define FLT_MIN (1.17549435e-38f)
#define DBL_MIN (2.2250738585072016e-308)
#define LDBL_MIN DBL_MIN
