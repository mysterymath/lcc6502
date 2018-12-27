/* Common definitions. */

/* The type of the result of subtracting two pointers. */
typedef int ptrdiff_t;

/* The type of the result of the sizeof operator. */
typedef unsigned int size_t;

/* The type of a wide character constant. */
typedef char wchar_t;

/* A null pointer constant. */
#define NULL ((void *)0)

/*
 * Returns an integral constant of type size_t. The value is the the offset in
 * bytes of the member designator from the beginning of a structure of the given
 * type.
 *
 * The following implementation only works since dereferencing a null pointer is
 * explicitly defined behavior by this implementation. The value is never used,
 * so it does not matter what is actually present at location zero.
 */
 #define offsetof(TYPE, MEMBER_DESIGNATOR) ((size_t)(&(((TYPE *)0)->MEMBER_DESIGNATOR)))