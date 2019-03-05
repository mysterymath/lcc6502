char foo(char a, char b) {
  return a + b;
}

char bar(char a, char b) {
  return a + b;
}

char baz(char a, char b) {
  __externally_visible();
  return a + b;
}

char nonrecursive(char a, char b) {
  __externally_visible();
  __interrupt();

  return foo(a, b);
}

char recursive(char a, char b) {
  __externally_visible();
  __recursive_interrupt();

  return bar(a, b);
}
