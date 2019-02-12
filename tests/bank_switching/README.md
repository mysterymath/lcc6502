# Bank Switching Test

This test ensures that the compiler can be used to generate code that can
operate in a bank-switched environment. The target is an OSS one-chip 16KB
cartridge for the Atari 800. This cartridge presents itself as only 8KB of
ROM; special accesses to the cartridge control which half of the 16KB is
accessible.