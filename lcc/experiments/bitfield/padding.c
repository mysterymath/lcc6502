/*
 * This experiment measures whether LCC inserts padding to align integers.
 * Result: No padding is inserted.
 */

struct bf {
    int a : 8;
    int b : 16;
};

int main(void) {
    return sizeof(struct bf);
}