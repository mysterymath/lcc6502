#include "test.h"

int bank3_fn_body(int a) {
  __externally_visible();
  __caller(bank3_fn);

  return a + 4;
}
