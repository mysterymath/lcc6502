/*
 * Measures what LCC generates for automatic struct variable initialization.
 */

struct s {
    int a;
    char b;
    char c;
};

int main(void) {
    struct s s1 = {1, 2};
    struct s s2 = {1, 2};
    struct s s3 = {1, 3};
    return s1.c;
}
