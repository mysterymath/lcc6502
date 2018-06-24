#define ATRACT (*(unsigned char*)0x4D)
void main(void) {
  ATRACT = 0x80;
  while(1)
    ;
}
