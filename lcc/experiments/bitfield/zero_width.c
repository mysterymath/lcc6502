struct bf {
    int a : 7;
    int : 0;
    int c : 1;
};

int main(void) {
    return sizeof(struct bf);
}