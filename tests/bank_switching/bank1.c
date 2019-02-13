#include "test.h"

int bank1_fn_body(int a) {
  __extern_call();
  return bank2_fn(a + 2);
}
