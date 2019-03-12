struct s {
  struct s* a;
  struct s* b;
} x = { &x, &x };
