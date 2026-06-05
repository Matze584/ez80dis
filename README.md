# ez80dis — eZ80 disassembler

A Python disassembler for the **Zilog eZ80** CPU, extending
[z80dis](https://github.com/lwerdna/z80dis) with full eZ80
instruction set support.

Found a bug? → [Open an issue!](https://github.com/Matze584/ez80dis/issues)

## Features

- All standard Z80 instructions
- All eZ80 additions: `LEA`, `PEA`, `MLT`, `TST`, `TSTIO`, `IN0`, `OUT0`,
  `SLP`, `STMIX`, `RSMIX`, extended block I/O (`INIM`/`OTIM`/`INI2`/… families)
- eZ80 16-bit `LD` variants
- ADL mode: 24-bit immediates and addresses
- `.lil`/`.lis`/`.sil`/`.sis` prefixes

## Installation

```
pip install ez80dis
```

## API

```python
from ez80dis import decode, disasm, Decoded, DECODE_STATUS

# Quick string — one call
print(disasm(bytes([0xDD, 0x54])))          # ld D,IXH

# Structured result
dec = decode(bytes([0x5B, 0xCD, 0x00, 0x10, 0x00]), addr=0x1000, adl=True)
print(dec.status)       # DECODE_STATUS.OK
print(dec.len)          # 5  (mode-prefix byte + CALL Opcode + 3-byte CALL target)
print(disasm(dec))      # call.lil 0x001000

# ADL mode active by default
dec = decode(bytes([0xC3, 0x00, 0x10, 0x00]), adl=True)
print(disasm(dec))      # jp 0x001000
```

### `decode(data, addr=0, adl=False) -> Decoded`

Decodes one instruction from `data` (bytes or list of ints).

| Field | Type | Description |
|---|---|---|
| `status` | `DECODE_STATUS` | `OK`, `INVALID_INSTRUCTION`, or `ERROR` |
| `len` | `int` | Number of bytes consumed |
| `op` | `OP` | Opcode enum value |
| `operands` | `list` | List of `(OPER_TYPE, value)` tuples |
| `typ` | `INSTRTYPE` | Instruction category |
| `mode_suffix` | `str` | `'.lil'` / `'.lis'` / `'.sil'` / `'.sis'` / `''` |
| `long_op` | `bool` | True when 24-bit operands are active |

### `disasm(data_or_decoded, pc=0, adl=False) -> str`

Convenience wrapper — accepts raw bytes or an already-decoded `Decoded` object.

### `FLAGS` — F-register decoder

`FLAGS` is an `IntFlag` enum for unpacking the Z80/eZ80 flags register:

| Bit | Name | Meaning |
|-----|------|---------|
| 0 | `C`  | Carry |
| 1 | `N`  | Add/subtract (set after SUB, cleared after ADD; used by DAA) |
| 2 | `PV` | Parity / Overflow |
| 3 | `F3` | Undocumented copy of result bit 3 |
| 4 | `H`  | Half-carry (carry from bit 3 to 4) |
| 5 | `F5` | Undocumented copy of result bit 5 |
| 6 | `Z`  | Zero |
| 7 | `S`  | Sign (MSB of A) |

```python
from ez80dis import FLAGS

f = FLAGS(0x45)          # e.g. value read from the F register
print(f.name)            # 'C|PV|Z'
print(FLAGS.Z in f)      # True
print(f & FLAGS.C)       # FLAGS.C
```

## License

Based on [z80dis](https://github.com/lwerdna/z80dis) by lwerdna.  
z80dis was released under [The Unlicense](UNLICENSE).
I decided to use the same for ez80dis. 
