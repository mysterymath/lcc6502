/* Variable Arguments */
#ifndef _STDARG_H
#define _STDARG_H

/*
 * A type suitable for holding information needed by va_start, va_arg, and
 * va_end.
 */
/* TODO: Determine the contents of this struct. */
typedef struct {int i;} va_list;

/* Initializes the va_list VA_LIST for further use by va_arg and va_end. */
#define va_start(VA_LIST, PARAM_N) (__builtin_va_start(&VA_LIST))

/*
 * Expands to an expression with the type and value of the next argument in the
 * call.
 */
#define va_arg(VA_LIST, TYPE) (*(TYPE*)__builtin_va_arg(&VA_LIST, sizeof(TYPE)))

/* Facilitates normal return from a function that invoked va_start. */
#define va_end(VA_LIST) 

#endif /* !defined(_STDARG_H) */