#include "test.h"

char accumulator = 1;

char bank1_fn_body(char i) {
  accumulator += i;
  return bank2_fn(i + 1)
}
