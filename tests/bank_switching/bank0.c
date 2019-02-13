#include "test.h"

void init(void) {
  __extern_call();
}

void start(void) {
  __extern_call();
  bank1_fn(1);
  while (1) {}
}