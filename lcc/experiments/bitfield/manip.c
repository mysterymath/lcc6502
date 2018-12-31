/*
 * This experiment measures how bit-fields are accessed and mutated, including
 * their bit order.
 *
 * Result:
 *
 * Bit-fields are allocated least significant bit first within a byte
 * (little-endian bit order).
 *
 * It seems even though sizeof(bf) is 1, it promotes an automatic variable of
 * that type to an int (2 bytes).
 *
 * Code effectively equivalent to the following C is emitted: int s; s |= 1;
 * return (s << 15) >> 15;
 */

struct bf {
    int a : 1;
};

int main(void) {
    struct bf s;
    s.a = 1;
    return s.a;
}