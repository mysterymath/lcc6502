# Prototype Plan

From analysis of the requirements and nature of the target platform, it's
clear that creating a C compiler for the 6502 is quite an undertaking. There
are a great number of edge and corner cases that need to be addressed, and
some fundamental theoretical difficulties as well. It's safe to say that at
present, we don't really know to generate good code for a platform like this
one in a principled, retargetable fashion, without resorting to essentially
brute-force search (or the more principled equivalents: constrant programming
and integer-linear programming).

Trying to resolve these theoretical difficulties and all the corner cases at
the same time is a non-starter. Thus, a prototype should be created to
discover how, in broad strokes, good code can be generated for the 6502.
Retargatability must necessarily be abandoned as a goal, but some of the
techniques used may prove useful for other similar architectures.

The purpose of such a prototype is to reduce the overall risk of the project.
Accordingly, it's scope must be carefully chosen to isolate as much risk as
possible, without taking on too much to make the problem intractible. Accordingly,
as much well-understood complexity as possible must be removed from the scope,
to avoid drowning the prototype in it.

As such, right off the bat, dealing with LCC's output or the C language is
out, as is converting from such a thing to internal IR. Non-SSA IRs are much
harder to use, and SSA conversion is inessential, so the IR should be
directly input to the prototype, already in SSA form. There's no need to
check that the program is in SSA form.

To minimize risk, the prototype should largely follow LLVM's latest approach,
unless reasons are discovered to do otherwise. This means gradually expanding
and reducing the SSA form until it consists of machine-synthesizable
instructions, then doing out-of-SSA transformation, register allocation, and
instruction scheduling, in some ordering, potentially phase-coupled.

Given that (roughtly) all programs for the 6502 need to exist in a span of
65,536 bytes, all programs are "smallish." Accordingly, whole-program techniques
can be used, and separate compilation is not an issue.

To take this to a logical extreme, an entire program can be put in SSA form,
as follows:

- Make all function calls basic block terminators.

- For a given function, number all basic blocks that are possible return
  addresses from that function.

- Reduce a function call to an assignment to the arguments and a
  specially-tagged branch (jsr). If the call is possibly recursive, precede it
  with a push of all live variables, and follow it with a similar pull.

- Reduce a function return as an assignment to a return location and a
  multiway branch (rts) to each return address based on a hidden variable.

The above algorithm should be part of the prototype, since it is untested and
risky.

Once a global SSA representation has been constructed, dominator trees need
to be constructed. This can't be input by the programmer, since the CFG will
have changed.

Afterwards, GVN-PRE should be performed. This one optimization pass subsumes
both GVN and PRE, without being much more difficult to implement than either.
PRE completely subsumes LICM, and GVN subsumes constant propagation and a
host of arithmetic simplifications. Together, one pass can do a huge swath of
optimization to the graph.

Then, 16-bit operations should be lowered to 8-bit operations, and another
round of GVN-PRE performed. GVN-PRE should be performed twice, since for
instance, a 16-bit comparison can be lowered two different ways. One is
generally more efficient, but the other has a chance to be unified with a
subtraction. The first GVN pass has a chance to do this unification before
the lower-er lowers the 16-bit comparison out of existence.

To determine the rest, an example that computes and displays prime numbers on
an Atari 800 should be constructed. The target format should be an XEX file,
for expediency. Using a real example like this is the only way to expose the
system to the real pressures of compiling an algorithm, without overloading
the problem too much with complexity.