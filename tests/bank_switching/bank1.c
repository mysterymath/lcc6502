#include "test.h"

int bank1_fn_body(int a) {
  __externally_visible();
  __caller(bank1_fn);

  return bank2_fn(a + 2);
}
