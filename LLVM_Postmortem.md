# LLVM Postmortem

Well, I gave it a real go. One of the first rules of software engineering,
really any kind of engineering, is "don't reinvent the wheel." To put it
another way, "don't rewrite LLVM, stupid." So, I've spent quite a while
learning LLVM, and trying to bend it to my will. It's not going to work.

So, to break down the usual advice a little bit, the primary *reason* not to
reinvent the wheel is that it's a lot of unnecessary work, you'll make
mistakes, your new wheel++ won't be battle tested or very round, etc etc. All
true, and I have no real objection to this. But, I failed that this reasoning
didn't *exactly* apply to my situation, since if LLVM is a wheel, it comes
with a whole car attached, and a road network too. I just need the wheel.

More concretely, LLVM deals with debugging, exception handling, computed
GOTOs, obscure GCC features, and the most obscure and piddling optimizations
known to the face of man. It's got to do it all, it's got to do it all
correctly, and it's all got to be *fast*. Don't get me wrong, that's great!
LLVM is a real achievement. But I spent a month trying to wedge a 6502
backend into the thing, and at the end of the month, all I had accomplished
was to get it to **not crash**.

Emitting nothing was a tremendous achievement all on its known, after almost
1000 lines of disabling this and that, since NO, my platform does not in
fact, have:

- A dynamic linker and associated relocatable object file format
- Debugging information
- Vector instructions
- A floating point module
- A calling convention
- Registers capable of holding pointers
- Yadda yadda

My platform does have:

- 3 tiny tiny 8-bit registers
- Heterogenous data paths (A<->X, A<->Y, but not X<->Y)
- Bizarre address modes
- An unusual BIT test operation
- Branches limited to at most 128 bytes away.
- A 256 byte stack, far too small for normal allocation

So, LLVM solves a million problems I don't have, and doesn't solve a million
problems I do. Sure, there's a lot of overlap, but the tiny sliver of savings
that provides doesn't come close to the work required just to turn everything
else *off*, let alone solve the hard problems of this platform at the same
time!