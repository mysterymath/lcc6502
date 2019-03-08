#include <setjmp.h>

char outer(jmp_buf jmp) {
  char c;

  if (c = setjmp(jmp)) {
    return c;
  }
  inner(jmp);
  return 0;
}

void inner(jmp_buf jmp) {
  longjmp(jmp, 1);
}