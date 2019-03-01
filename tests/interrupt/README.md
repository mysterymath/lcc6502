# Interrupt Test

This test ensures that the compiler can be used to generate code that can run
inside an Atari800 interrupt handler. This must be true for both critical
sections with interrupts disabled and slower interrupt sections that could
themselves be interrupted.e., may be recursive). The interrupts must not
conflict with one another, themselves, or regular code.
