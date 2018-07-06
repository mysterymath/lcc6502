#define IOCB0 (*(IOCB*)0x0340)
#define PUT_CHARACTERS 0x0B
#define CIOV ((void*)0xE456)

#define __a 0
#define __x 1

void __asm_call(void* address, ...);

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
  IOCB0.BA = 0;
  __asm_call(CIOV, __x, 0, __a, 'A');
  while(1)
    ;
}
