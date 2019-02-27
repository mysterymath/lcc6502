#include <stdarg.h>

int usr(char argc, ...) {
  va_list args;
  char result;
  char i;

  __externally_visible();
  
  va_start(argc, argc);

  result = va_arg(argc, int);
  for (i = 1; i < argc; i++) {
    result -= va_arg(args, int);
  }

  va_end(args);

  return result;
}
