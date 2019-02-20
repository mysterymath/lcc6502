#include "test.h"

char bank1_fn_body(char a);
char bank2_fn_body(char a);
char bank3_fn_body(char a);

char bank1_fn(char a) {
  __asm_call();
  __clobbers("NZV");
  __calls(bank1_fn_body);
}

char bank2_fn(char a) {
  __asm_call();
  __clobbers("NZV");
  __calls(bank2_fn_body);
}

char bank3_fn(char a) {
  __asm_call();
  __clobbers("NZV");
  __calls(bank3_fn_body);
}

void init(void) {
  __externally_visible();
}

void start(void) {
  __externally_visible();

  bank1_fn(1);
  while (1) {}
}