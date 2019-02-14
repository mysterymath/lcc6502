#include "test.h"

int bank2_fn_body(int a) {
  __extern_call();
  __caller(bank2_fn);

  return bank3_fn(a + 3);
}
