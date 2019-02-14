#include "test.h"

int bank3_fn_body(int a) {
  __extern_call();
  __caller(bank3_fn);

  return a + 4;
}
