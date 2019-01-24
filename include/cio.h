/* Atari 800 CIO (Central I/O Utility) API */

#ifndef CIO_H
#define CIO_H

struct IOCB {
    /* Handler ID */
    unsigned char HID;

    /* Device Number */
    unsigned char DNO;

    /* Command Byte */
    unsigned char CMD;

    /* Status */
    unsigned char STA;

    /* Buffer Address */
    const void *BA;

    /* PUT Address */
    const void *PT;

    /* Buffer Length/Byte Count */
    unsigned int BL;

    /* Auxiliary Information */
    unsigned char AX[6];
} *IOCB = (struct IOCB*)0x340;

#define OPEN_CMD 0x03
#define CLOSE_CMD 0x0C
#define GET_CHARACTERS_CMD 0x07

#endif /* !defined(CIO_H) */
