struct bf {
    int a : 1;
};

int main(void) {
    struct bf s;
    s.a = 1;
    return s.a;
}