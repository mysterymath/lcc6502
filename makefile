# $Id$
BUILDDIR=build
A=.a
O=.o
E=
CC=cc
CFLAGS=-g
LDFLAGS=-g
LD=$(CC)
AR=ar ruv
RANLIB=ranlib
DIFF=diff
RM=rm -f
TSTDIR=$(BUILDDIR)/$(TARGET)/tst
CUSTOM=custom.mk
include $(CUSTOM)
B=$(BUILDDIR)/
T=$(TSTDIR)/

what:
	-@echo make all rcc cpp lcc bprint liblcc clean clobber

all::	rcc cpp lcc bprint liblcc

rcc:	$Brcc$E
cpp:	$Bcpp$E
lcc:	$Blcc$E
bprint:	$Bbprint$E
liblcc:	$Bliblcc$A

RCCOBJS=$Balloc$O \
	$Bbind$O \
	$Bdag$O \
	$Bdecl$O \
	$Benode$O \
	$Berror$O \
	$Bexpr$O \
	$Bevent$O \
	$Binit$O \
	$Binits$O \
	$Binput$O \
	$Blex$O \
	$Blist$O \
	$Bmain$O \
	$Boutput$O \
	$Bprof$O \
	$Bprofio$O \
	$Bsimp$O \
	$Bstmt$O \
	$Bstring$O \
	$Bsym$O \
	$Btrace$O \
	$Btree$O \
	$Btypes$O \
	$Bnull$O \
	$Bgen$O \
	$Bbytecode$O

$Brcc$E::	$Bmain$O $Blibrcc$A $(EXTRAOBJS)
		$(LD) $(LDFLAGS) -o $@ $Bmain$O $(EXTRAOBJS) $Blibrcc$A $(EXTRALIBS)

$Blibrcc$A:	$(RCCOBJS)
		$(AR) $@ $(RCCOBJS); $(RANLIB) $@ || true

$(RCCOBJS):	src/c.h src/ops.h src/token.h src/config.h

$Balloc$O:	src/alloc.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/alloc.c
$Bbind$O:	src/bind.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/bind.c
$Bdag$O:	src/dag.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/dag.c
$Bdecl$O:	src/decl.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/decl.c
$Benode$O:	src/enode.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/enode.c
$Berror$O:	src/error.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/error.c
$Bevent$O:	src/event.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/event.c
$Bexpr$O:	src/expr.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/expr.c
$Bgen$O:	src/gen.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/gen.c
$Binit$O:	src/init.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/init.c
$Binits$O:	src/inits.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/inits.c
$Binput$O:	src/input.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/input.c
$Blex$O:	src/lex.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/lex.c
$Blist$O:	src/list.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/list.c
$Bmain$O:	src/main.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/main.c
$Bnull$O:	src/null.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/null.c
$Boutput$O:	src/output.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/output.c
$Bprof$O:	src/prof.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/prof.c
$Bprofio$O:	src/profio.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/profio.c
$Bsimp$O:	src/simp.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/simp.c
$Bstmt$O:	src/stmt.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/stmt.c
$Bstring$O:	src/string.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/string.c
$Bsym$O:	src/sym.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/sym.c
$Bbytecode$O:	src/bytecode.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/bytecode.c
$Btrace$O:	src/trace.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/trace.c
$Btree$O:	src/tree.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/tree.c
$Btypes$O:	src/types.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/types.c
$Bstab$O:	src/stab.c src/stab.h;	$(CC) $(CFLAGS) -c -Isrc -o $@ src/stab.c

$Bbprint$E:	$Bbprint$O;		$(LD) $(LDFLAGS) -o $@ $Bbprint$O 
$Bops$E:	$Bops$O;		$(LD) $(LDFLAGS) -o $@ $Bops$O 

$Bbprint$O:	etc/bprint.c src/profio.c;	$(CC) $(CFLAGS) -c -Isrc -o $@ etc/bprint.c
$Bops$O:	etc/ops.c src/ops.h;		$(CC) $(CFLAGS) -c -Isrc -o $@ etc/ops.c

$Blcc$E:	$Blcc$O $Bhost$O;	$(LD) $(LDFLAGS) -o $@ $Blcc$O $Bhost$O 

$Blcc$O:	etc/lcc.c;		$(CC) $(CFLAGS) -c -o $@ etc/lcc.c
$Bhost$O:	$(HOSTFILE);	$(CC) $(CFLAGS) -c -o $@ $(HOSTFILE)

LIBOBJS=$Bassert$O $Bbbexit$O $Byynull$O

$Bliblcc$A:	$(LIBOBJS);	$(AR) $@ $Bassert$O $Bbbexit$O $Byynull$O; $(RANLIB) $@ || true

$Bassert$O:	lib/assert.c;	$(CC) $(CFLAGS) -c -o $@ lib/assert.c
$Byynull$O:	lib/yynull.c;	$(CC) $(CFLAGS) -c -o $@ lib/yynull.c
$Bbbexit$O:	lib/bbexit.c;	$(CC) $(CFLAGS) -c -o $@ lib/bbexit.c

CPPOBJS=$Bcpp$O $Blexer$O $Bnlist$O $Btokens$O $Bmacro$O $Beval$O \
	$Binclude$O $Bhideset$O $Bgetopt$O $Bunix$O

$Bcpp$E:	$(CPPOBJS)
		$(LD) $(LDFLAGS) -o $@ $(CPPOBJS) 

$(CPPOBJS):	cpp/cpp.h

$Bcpp$O:	cpp/cpp.c;	$(CC) $(CFLAGS) -c -Icpp -o $@ cpp/cpp.c
$Blexer$O:	cpp/lex.c;	$(CC) $(CFLAGS) -c -Icpp -o $@ cpp/lex.c
$Bnlist$O:	cpp/nlist.c;	$(CC) $(CFLAGS) -c -Icpp -o $@ cpp/nlist.c
$Btokens$O:	cpp/tokens.c;	$(CC) $(CFLAGS) -c -Icpp -o $@ cpp/tokens.c
$Bmacro$O:	cpp/macro.c;	$(CC) $(CFLAGS) -c -Icpp -o $@ cpp/macro.c
$Beval$O:	cpp/eval.c;	$(CC) $(CFLAGS) -c -Icpp -o $@ cpp/eval.c
$Binclude$O:	cpp/include.c;	$(CC) $(CFLAGS) -c -Icpp -o $@ cpp/include.c
$Bhideset$O:	cpp/hideset.c;	$(CC) $(CFLAGS) -c -Icpp -o $@ cpp/hideset.c
$Bgetopt$O:	cpp/getopt.c;	$(CC) $(CFLAGS) -c -Icpp -o $@ cpp/getopt.c
$Bunix$O:	cpp/unix.c;	$(CC) $(CFLAGS) -c -Icpp -o $@ cpp/unix.c

clean::
		$(RM) $B*$O
		$(RM) $Brcc1$E $Brcc1$E $B1rcc$E $B2rcc$E
		$(RM) $B*.ilk

clobber::	clean
		$(RM) $Brcc$E $Bcpp$E $Blcc$E $Bcp$E $Bbprint$E $B*$A
		$(RM) $B*.pdb $B*.pch

RCCSRCS=src/alloc.c \
	src/bind.c \
	src/dag.c \
	src/decl.c \
	src/enode.c \
	src/error.c \
	src/expr.c \
	src/event.c \
	src/init.c \
	src/inits.c \
	src/input.c \
	src/lex.c \
	src/list.c \
	src/main.c \
	src/output.c \
	src/prof.c \
	src/profio.c \
	src/simp.c \
	src/stmt.c \
	src/string.c \
	src/sym.c \
	src/trace.c \
	src/tree.c \
	src/types.c \
	src/null.c \
	src/bytecode.c \
	src/gen.c \
	src/stab.c

C=$Blcc -A -d0.6 -Wo-lccdir=$(BUILDDIR) -Isrc -I$(BUILDDIR)
triple:	$B2rcc$E
	strip $B1rcc$E $B2rcc$E
	dd if=$B1rcc$E of=$Brcc1$E bs=512 skip=1
	dd if=$B2rcc$E of=$Brcc2$E bs=512 skip=1
	if cmp $Brcc1$E $Brcc2$E; then \
		mv $B2rcc$E $Brcc$E; \
		$(RM) $B1rcc$E $Brcc[12]$E; fi

$B1rcc$E:	$Brcc$E $Blcc$E $Bcpp$E
		$C -o $@ -B$B $(RCCSRCS)
$B2rcc$E:	$B1rcc$E
		$C -o $@ -B$B1 $(RCCSRCS)
