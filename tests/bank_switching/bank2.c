#include "test.h"

char bank2_fn_body(char a) {
  __externally_visible();
  __caller(bank2_fn);

  return bank3_fn(a + 3);
}
