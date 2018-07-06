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

void main(void) {
  IOCB0.CMD = PUT_CHARACTERS;
  IOCB0.BL = 0;
  __asm_call(CIOV, 'H', 0, -1);
  __asm_call(CIOV, 'e', 0, -1);
  __asm_call(CIOV, 'l', 0, -1);
  __asm_call(CIOV, 'l', 0, -1);
  __asm_call(CIOV, 'o', 0, -1);
  __asm_call(CIOV, ',', 0, -1);
  __asm_call(CIOV, ' ', 0, -1);
  __asm_call(CIOV, 'W', 0, -1);
  __asm_call(CIOV, 'o', 0, -1);
  __asm_call(CIOV, 'r', 0, -1);
  __asm_call(CIOV, 'l', 0, -1);
  __asm_call(CIOV, 'd', 0, -1);
  __asm_call(CIOV, '!', 0, -1);
  while(1)
    ;
}
