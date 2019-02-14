#include "test.h"

void init(void) {
  __externally_visible();
  __entry();
}

void start(void) {
  __externally_visible();
  __entry();

  bank1_fn(1);
  while (1) {}
}