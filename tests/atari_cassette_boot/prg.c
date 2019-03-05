#define PACTL (*(char*)0xD302)
#define DOSVEC (*(void**)0xA)
#define MEMLO (*(void**)0xE)
#define APPMHI (*(void**)0x2E7)

extern char start;
extern char end;

char boot(void) {
  __externally_visible();
  // Due to a system bug, the cassette drive must be stopped manually.
  PACTL = 0x3C;

  DOSVEC = &start;
  MEMLO = APPMHI = &end;
  return 0;
}

void init(void) {
  __externally_visible();
}

char test(void) {
  __externally_visible();

  return 0x0A;
}
