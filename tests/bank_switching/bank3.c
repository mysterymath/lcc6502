#include "test.h"

char bank3_fn_body(char a) {
  __externally_visible();
  __caller(bank3_fn);

  return a + 4;
}
