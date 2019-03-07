# Design Rationale

* Prototypes in library headers may only use identifiers in the reserved
    namespace (`__x` or `_X`). Otherwise, the user could place a #define macro
    before the header as follows:

```C
#define status []
void exit(int status);
```

This becomes:

```C
void exit(int []);
```