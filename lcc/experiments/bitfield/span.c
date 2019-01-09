struct bf {
    int a : 15;
    int b : 16;
    int c : 1;
};

int main(void) {
    return sizeof(struct bf);
}
