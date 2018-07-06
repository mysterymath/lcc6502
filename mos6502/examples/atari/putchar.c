#define IOCB0 (*(IOCB*)0x0340)
#define PUT_CHARACTERS 0x0B
#define CIOV ((void*)0xE456)

void __begin_asm(void);
void __end_asm(void);
void __ldx(unsigned char x);
void __lda(unsigned char a);
void __jsr(void* destination);

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
  __begin_asm();
  __ldx(0);
  __lda('A');
  __jsr(CIOV);
  __end_asm();
  while(1)
    ;
}
