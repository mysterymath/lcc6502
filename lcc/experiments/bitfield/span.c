/*
 * This experiment measures whether LCC allows bitfields to span byte boundaries.
 * Result: LCC allows bit fields to span byte boundaries.
 */

struct bf {
    int a : 7;
    int b : 8;
    int c : 1;
};

int main(void) {
    return sizeof(struct bf);
}