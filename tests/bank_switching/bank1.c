#include "test.h"

char bank1_fn_body(char a) {
  __externally_visible();
  __caller(bank1_fn);

  return bank2_fn(a + 2);
}
