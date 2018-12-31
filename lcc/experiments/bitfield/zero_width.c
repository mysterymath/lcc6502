/*
 * This experiment tests the semantics of zero-width bitfields.
 *
 * Result: Zero width bitfields force moving to the next byte, as required by
 * the standard.
 */

struct bf {
    int a : 7;
    int : 0;
    int c : 1;
};

int main(void) {
    return sizeof(struct bf);
}