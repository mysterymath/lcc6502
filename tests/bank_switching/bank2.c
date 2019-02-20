#include "test.h"

char bank2_fn_body(char i) {
  accumulator += i;
  return bank3_fn(i + 1);
}
