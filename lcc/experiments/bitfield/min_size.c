/*
 * This experiment measures the minimum size of a struct containing a bitfield.
 * Result: 1 byte.
 */

struct bf {
    int a : 1;
};

int main(void) {
    return sizeof(struct bf);
}