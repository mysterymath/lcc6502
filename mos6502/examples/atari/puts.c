#define IOCB0 (*(IOCB*)0x0340)
#define PUT_CHARACTERS 0x0B
#define CIOV ((void*)0xE456)

void __asm_call(void* address, int a, int x, int y);

typedef struct {
  unsigned char HID;
  unsigned char DNO;
  unsigned char CMD;
  unsigned char STA;
  void* BA; 
  void* PT;
  unsigned short BL;
  unsigned char AX[6];
} IOCB;

void begin_putchar(void) {
  IOCB0.CMD = PUT_CHARACTERS;
  IOCB0.BL = 0;
}

void putchar(char c) {
  __asm_call(CIOV, c, 0, -1);
}

void main(void) {
  char* s = "Hello, world!";

  begin_putchar();
  while (*s) {
    putchar(*s++);
  }
  while(1)
    ;
}
