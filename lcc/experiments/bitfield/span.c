struct bf {
    int a : 7;
    int b : 8;
    int c : 1;
};

int main(void) {
    return sizeof(struct bf);
}