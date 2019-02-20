#include "test.h"

char bank1_fn_body(char i);
char bank2_fn_body(char i);
char bank3_fn_body(char i);

char bank1_fn(char i) {
  __external();
  __clobbers("NZV");
  __calls(bank1_fn_body);
}

char bank2_fn(char i) {
  __external();
  __clobbers("NZV");
  __calls(bank2_fn_body);
}

char bank3_fn(char i) {
  __external();
  __clobbers("NZV");
  __calls(bank3_fn_body);
}

void main(void) {
  __externally_visible();

  bank1_fn(2);
  while (1) {}
}