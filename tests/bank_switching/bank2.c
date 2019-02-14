#include "test.h"

int bank2_fn_body(int a) {
  __externally_visible();
  __caller(bank2_fn);

  return bank3_fn(a + 3);
}
