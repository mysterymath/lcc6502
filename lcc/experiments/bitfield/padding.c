struct bf {
    int a : 8;
    int b : 16;
};

int main(void) {
    return sizeof(struct bf);
}