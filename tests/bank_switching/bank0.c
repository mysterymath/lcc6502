#include "test.h"

void init(void) {
  __extern_call();
  __entry();
}

void start(void) {
  __extern_call();
  __entry();

  bank1_fn(1);
  while (1) {}
}