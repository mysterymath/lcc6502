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

void putchar(unsigned char c) {
  __asm_call(CIOV, c, 0, -1);
}

void main(void) {
  begin_putchar();
  putchar('H');
  putchar('e');
  putchar('l');
  putchar('l');
  putchar('o');
  putchar(',');
  putchar(' ');
  putchar('W');
  putchar('o');
  putchar('r');
  putchar('l');
  putchar('d');
  putchar('!');
  while(1)
    ;
}
