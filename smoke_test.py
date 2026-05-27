#!/usr/bin/env python3
"""Smoke test for ez80dis — checks that known byte sequences disassemble to expected mnemonics."""

import sys
from ez80dis import decode, disasm, DECODE_STATUS

PASS = 0
FAIL = 0

def check(label, data, expected, adl=False):
    global PASS, FAIL
    data = bytes(data)
    dec = decode(data, adl=adl)
    got = disasm(dec, adl=adl)
    hex_str = ' '.join('%02X' % b for b in data[:dec.len])
    ok = got == expected
    status = 'OK  ' if ok else 'FAIL'
    print(f'  {status}  {hex_str:<20s}  {got:<30s}', end='')
    if not ok:
        print(f'  expected: {expected}', end='')
        FAIL += 1
    else:
        PASS += 1
    print()

def section(title):
    print(f'\n{"="*60}')
    print(f'  {title}')
    print(f'{"="*60}')

# ---------------------------------------------------------------------------
section('NOP / HALT / misc CPU control')
# ---------------------------------------------------------------------------
check('NOP',        [0x00],             'nop')
check('HALT',       [0x76],             'halt')
check('DI',         [0xF3],             'di')
check('EI',         [0xFB],             'ei')
check('IM 0',       [0xED, 0x46],       'im 0')
check('IM 1',       [0xED, 0x56],       'im 1')
check('IM 2',       [0xED, 0x5E],       'im 2')
check('RETI',       [0xED, 0x4D],       'reti')
check('RETN',       [0xED, 0x45],       'retn')

# ---------------------------------------------------------------------------
section('8-bit loads — LD r,r / LD r,n / LD r,(HL)')
# ---------------------------------------------------------------------------
check('LD A,B',     [0x78],             'ld A,B')
check('LD B,C',     [0x41],             'ld B,C')
check('LD D,H',     [0x54],             'ld D,H')
check('LD A,n',     [0x3E, 0x42],       'ld A,0x42')
check('LD B,n',     [0x06, 0x00],       'ld B,0')
check('LD A,(HL)',  [0x7E],             'ld A,(HL)')
check('LD (HL),A',  [0x77],             'ld (HL),A')
check('LD (HL),n',  [0x36, 0xFF],       'ld (HL),0xff')
check('LD A,I',     [0xED, 0x57],       'ld A,I')
check('LD I,A',     [0xED, 0x47],       'ld I,A')
check('LD A,R',     [0xED, 0x5F],       'ld A,R')
check('LD R,A',     [0xED, 0x4F],       'ld R,A')

# ---------------------------------------------------------------------------
section('8-bit loads — IX/IY displacement')
# ---------------------------------------------------------------------------
check('LD A,(IX+0)',  [0xDD, 0x7E, 0x00], 'ld A,(IX+0)')
check('LD A,(IX+5)',  [0xDD, 0x7E, 0x05], 'ld A,(IX+5)')
check('LD A,(IX-1)',  [0xDD, 0x7E, 0xFF], 'ld A,(IX-1)')
check('LD A,(IY+0)',  [0xFD, 0x7E, 0x00], 'ld A,(IY+0)')
check('LD (IX+0),A',  [0xDD, 0x77, 0x00], 'ld (IX+0),A')
check('LD (IX+3),n',  [0xDD, 0x36, 0x03, 0xAB], 'ld (IX+3),0xab')

# ---------------------------------------------------------------------------
section('16-bit loads')
# ---------------------------------------------------------------------------
check('LD BC,nn',   [0x01, 0x34, 0x12], 'ld BC,0x1234')
check('LD DE,nn',   [0x11, 0x34, 0x12], 'ld DE,0x1234')
check('LD HL,nn',   [0x21, 0x34, 0x12], 'ld HL,0x1234')
check('LD SP,nn',   [0x31, 0x34, 0x12], 'ld SP,0x1234')
check('LD SP,HL',   [0xF9],             'ld SP,HL')
check('LD (nn),HL', [0x22, 0x00, 0x10], 'ld (0x1000),HL')
check('LD HL,(nn)', [0x2A, 0x00, 0x10], 'ld HL,(0x1000)')
check('LD (nn),A',  [0x32, 0x00, 0x10], 'ld (0x1000),A')
check('LD A,(nn)',  [0x3A, 0x00, 0x10], 'ld A,(0x1000)')
check('PUSH BC',    [0xC5],             'push BC')
check('POP HL',     [0xE1],             'pop HL')

# ---------------------------------------------------------------------------
section('Register exchange')
# ---------------------------------------------------------------------------
check('EX DE,HL',   [0xEB],             'ex DE,HL')
check('EX AF,AF\'', [0x08],             "ex AF,AF'")
check('EXX',        [0xD9],             'exx')

# ---------------------------------------------------------------------------
section('Arithmetic / logic')
# ---------------------------------------------------------------------------
check('ADD A,B',    [0x80],             'add A,B')
check('ADD A,n',    [0xC6, 0x10],       'add A,0x10')
check('ADC A,C',    [0x89],             'adc A,C')
check('SUB D',      [0x92],             'sub D')
check('SBC A,E',    [0x9B],             'sbc A,E')
check('AND H',      [0xA4],             'and H')
check('OR L',       [0xB5],             'or L')
check('XOR A',      [0xAF],             'xor A')
check('CP B',       [0xB8],             'cp B')
check('INC A',      [0x3C],             'inc A')
check('DEC B',      [0x05],             'dec B')
check('INC HL',     [0x23],             'inc HL')
check('DEC DE',     [0x1B],             'dec DE')
check('ADD HL,BC',  [0x09],             'add HL,BC')
check('ADC HL,DE',  [0xED, 0x5A],       'adc HL,DE')
check('SBC HL,SP',  [0xED, 0x72],       'sbc HL,SP')
check('NEG',        [0xED, 0x44],       'neg')
check('DAA',        [0x27],             'daa')
check('CPL',        [0x2F],             'cpl')
check('SCF',        [0x37],             'scf')
check('CCF',        [0x3F],             'ccf')

# ---------------------------------------------------------------------------
section('Rotates / shifts')
# ---------------------------------------------------------------------------
check('RLCA',       [0x07],             'rlca')
check('RRCA',       [0x0F],             'rrca')
check('RLA',        [0x17],             'rla')
check('RRA',        [0x1F],             'rra')
check('RLC B',      [0xCB, 0x00],       'rlc B')
check('RRC C',      [0xCB, 0x09],       'rrc C')
check('RL D',       [0xCB, 0x12],       'rl D')
check('RR E',       [0xCB, 0x1B],       'rr E')
check('SLA H',      [0xCB, 0x24],       'sla H')
check('SRA L',      [0xCB, 0x2D],       'sra L')
check('SRL A',      [0xCB, 0x3F],       'srl A')
check('RLC (HL)',    [0xCB, 0x06],       'rlc (HL)')
check('RLC (IX+0)', [0xDD, 0xCB, 0x00, 0x06], 'rlc (IX+0)')
check('RLC (IX+2)', [0xDD, 0xCB, 0x02, 0x06], 'rlc (IX+2)')
check('RLD',        [0xED, 0x6F],       'rld')
check('RRD',        [0xED, 0x67],       'rrd')

# ---------------------------------------------------------------------------
section('Bit manipulation')
# ---------------------------------------------------------------------------
check('BIT 0,A',    [0xCB, 0x47],       'bit 0,A')
check('BIT 7,H',    [0xCB, 0x7C],       'bit 7,H')
check('SET 3,B',    [0xCB, 0xD8],       'set 3,B')
check('RES 5,(HL)', [0xCB, 0xAE],       'res 5,(HL)')
check('BIT 2,(IX+0)',[0xDD,0xCB,0x00,0x56], 'bit 2,(IX+0)')
check('SET 1,(IY+3)',[0xFD,0xCB,0x03,0xCE], 'set 1,(IY+3)')

# ---------------------------------------------------------------------------
section('Jumps / calls / returns')
# ---------------------------------------------------------------------------
check('JP nn',      [0xC3, 0x00, 0x10], 'jp 0x1000')
check('JP Z,nn',    [0xCA, 0x00, 0x10], 'jp z,0x1000')
check('JP NZ,nn',   [0xC2, 0x00, 0x10], 'jp nz,0x1000')
check('JP (HL)',    [0xE9],             'jp (HL)')
check('JP (IX)',    [0xDD, 0xE9],       'jp (IX)')
check('JR e',       [0x18, 0x00],       'jr 0x0002')   # pc=0, offset=0 → 0+2+0=2
check('JR Z,e',     [0x28, 0xFE],       'jr z,0x0000') # offset=-2 → 0+2-2=0
check('DJNZ e',     [0x10, 0x00],       'djnz 0x0002')
check('CALL nn',    [0xCD, 0x00, 0x10], 'call 0x1000')
check('CALL Z,nn',  [0xCC, 0x00, 0x10], 'call z,0x1000')
check('RET',        [0xC9],             'ret')
check('RET NZ',     [0xC0],             'ret nz')
check('RST 00h',    [0xC7],             'rst 0')
check('RST 38h',    [0xFF],             'rst 0x38')

# ---------------------------------------------------------------------------
section('Block transfer / search')
# ---------------------------------------------------------------------------
check('LDI',        [0xED, 0xA0],       'ldi')
check('LDD',        [0xED, 0xA8],       'ldd')
check('LDIR',       [0xED, 0xB0],       'ldir')
check('LDDR',       [0xED, 0xB8],       'lddr')
check('CPI',        [0xED, 0xA1],       'cpi')
check('CPD',        [0xED, 0xA9],       'cpd')
check('CPIR',       [0xED, 0xB1],       'cpir')
check('CPDR',       [0xED, 0xB9],       'cpdr')

# ---------------------------------------------------------------------------
section('I/O')
# ---------------------------------------------------------------------------
check('IN A,(n)',   [0xDB, 0x01],       'in A,(0x01)')
check('OUT (n),A',  [0xD3, 0x01],       'out (0x01),A')
check('IN B,(C)',   [0xED, 0x40],       'in B,(C)')
check('OUT (C),D',  [0xED, 0x51],       'out (C),D')
check('INI',        [0xED, 0xA2],       'ini')
check('OUTI',       [0xED, 0xA3],       'outi')
check('INIR',       [0xED, 0xB2],       'inir')
check('OTIR',       [0xED, 0xB3],       'otir')
check('IND',        [0xED, 0xAA],       'ind')
check('OUTD',       [0xED, 0xAB],       'outd')
check('INDR',       [0xED, 0xBA],       'indr')
check('OTDR',       [0xED, 0xBB],       'otdr')

# ---------------------------------------------------------------------------
section('eZ80 — LEA / PEA')
# ---------------------------------------------------------------------------
check('LEA BC,IX+0',  [0xED, 0x02, 0x00], 'lea BC,IX+0')
check('LEA BC,IY+0',  [0xED, 0x03, 0x00], 'lea BC,IY+0')
check('LEA DE,IX+0',  [0xED, 0x12, 0x00], 'lea DE,IX+0')
check('LEA DE,IY+5',  [0xED, 0x13, 0x05], 'lea DE,IY+5')
check('LEA HL,IX+0',  [0xED, 0x22, 0x00], 'lea HL,IX+0')
check('LEA IX,IX+0',  [0xED, 0x32, 0x00], 'lea IX,IX+0')
check('LEA IY,IY+0',  [0xED, 0x33, 0x00], 'lea IY,IY+0')
check('LEA IX,IY+0',  [0xED, 0x54, 0x00], 'lea IX,IY+0')
check('LEA IY,IX+0',  [0xED, 0x55, 0x00], 'lea IY,IX+0')
check('PEA IX+0',     [0xED, 0x65, 0x00], 'pea IX+0')
check('PEA IY+3',     [0xED, 0x66, 0x03], 'pea IY+3')

# ---------------------------------------------------------------------------
section('eZ80 — IN0 / OUT0 / TST / TSTIO')
# ---------------------------------------------------------------------------
check('IN0 B,(n)',   [0xED, 0x00, 0x10], 'in0 B,(0x10)')
check('IN0 C,(n)',   [0xED, 0x08, 0x10], 'in0 C,(0x10)')
check('IN0 A,(n)',   [0xED, 0x38, 0x10], 'in0 A,(0x10)')
check('OUT0 (n),B',  [0xED, 0x01, 0x10], 'out0 (0x10),B')
check('OUT0 (n),A',  [0xED, 0x39, 0x10], 'out0 (0x10),A')
check('TST A,B',     [0xED, 0x04],       'tst A,B')
check('TST A,(HL)',  [0xED, 0x34],       'tst A,(HL)')
check('TST A,A',     [0xED, 0x3C],       'tst A,A')
check('TST A,n',     [0xED, 0x64, 0x55], 'tst A,0x55')
check('TSTIO n',     [0xED, 0x74, 0x55], 'tstio 0x55')

# ---------------------------------------------------------------------------
section('eZ80 — MLT')
# ---------------------------------------------------------------------------
check('MLT BC',     [0xED, 0x4C],       'mlt BC')
check('MLT DE',     [0xED, 0x5C],       'mlt DE')
check('MLT HL',     [0xED, 0x6C],       'mlt HL')
check('MLT SP',     [0xED, 0x7C],       'mlt SP')

# ---------------------------------------------------------------------------
section('eZ80 — LD MB / SLP / STMIX / RSMIX')
# ---------------------------------------------------------------------------
check('LD MB,A',    [0xED, 0x6D],       'ld MB,A')
check('LD A,MB',    [0xED, 0x6E],       'ld A,MB')
check('SLP',        [0xED, 0x76],       'slp')
check('STMIX',      [0xED, 0x7D],       'stmix')
check('RSMIX',      [0xED, 0x7E],       'rsmix')

# ---------------------------------------------------------------------------
section('eZ80 — 16-bit LD via (HL)')
# ---------------------------------------------------------------------------
check('LD BC,(HL)', [0xED, 0x07],       'ld BC,(HL)')
check('LD DE,(HL)', [0xED, 0x17],       'ld DE,(HL)')
check('LD HL,(HL)', [0xED, 0x27],       'ld HL,(HL)')
check('LD IX,(HL)', [0xED, 0x37],       'ld IX,(HL)')
check('LD IY,(HL)', [0xED, 0x31],       'ld IY,(HL)')
check('LD (HL),BC', [0xED, 0x0F],       'ld (HL),BC')
check('LD (HL),DE', [0xED, 0x1F],       'ld (HL),DE')
check('LD (HL),HL', [0xED, 0x2F],       'ld (HL),HL')
check('LD (HL),IX', [0xED, 0x3F],       'ld (HL),IX')
check('LD (HL),IY', [0xED, 0x3E],       'ld (HL),IY')
check('LD I,HL',    [0xED, 0xC7],       'ld I,HL')
check('LD HL,I',    [0xED, 0xD7],       'ld HL,I')

# ---------------------------------------------------------------------------
section('eZ80 — 16-bit LD via (IX+d) / (IY+d)')
# ---------------------------------------------------------------------------
check('LD BC,(IX+0)', [0xDD, 0x07, 0x00], 'ld BC,(IX+0)')
check('LD DE,(IX+0)', [0xDD, 0x17, 0x00], 'ld DE,(IX+0)')
check('LD HL,(IX+0)', [0xDD, 0x27, 0x00], 'ld HL,(IX+0)')
check('LD IY,(IX+0)', [0xDD, 0x31, 0x00], 'ld IY,(IX+0)')
check('LD IX,(IX+0)', [0xDD, 0x37, 0x00], 'ld IX,(IX+0)')
check('LD (IX+0),BC', [0xDD, 0x0F, 0x00], 'ld (IX+0),BC')
check('LD (IX+0),DE', [0xDD, 0x1F, 0x00], 'ld (IX+0),DE')
check('LD (IX+0),HL', [0xDD, 0x2F, 0x00], 'ld (IX+0),HL')
check('LD (IX+0),IY', [0xDD, 0x3E, 0x00], 'ld (IX+0),IY')
check('LD (IX+0),IX', [0xDD, 0x3F, 0x00], 'ld (IX+0),IX')
check('LD BC,(IY+0)', [0xFD, 0x07, 0x00], 'ld BC,(IY+0)')
check('LD IX,(IY+0)', [0xFD, 0x31, 0x00], 'ld IX,(IY+0)')

# ---------------------------------------------------------------------------
section('eZ80 — Extended block I/O')
# ---------------------------------------------------------------------------
check('INIRX',      [0xED, 0xC2],       'inirx')
check('OTIRX',      [0xED, 0xC3],       'otirx')
check('INDRX',      [0xED, 0xCA],       'indrx')
check('OTDRX',      [0xED, 0xCB],       'otdrx')
check('INIM',       [0xED, 0x82],       'inim')
check('INDM',       [0xED, 0x8A],       'indm')
check('INIMR',      [0xED, 0x92],       'inimr')
check('INDMR',      [0xED, 0x9A],       'indmr')
check('OTIM',       [0xED, 0x83],       'otim')
check('OTDM',       [0xED, 0x8B],       'otdm')
check('OTIMR',      [0xED, 0x93],       'otimr')
check('OTDMR',      [0xED, 0x9B],       'otdmr')
check('INI2',       [0xED, 0x84],       'ini2')
check('IND2',       [0xED, 0x8C],       'ind2')
check('INI2R',      [0xED, 0x94],       'ini2r')
check('IND2R',      [0xED, 0x9C],       'ind2r')
check('OUTI2',      [0xED, 0xA4],       'outi2')
check('OUTD2',      [0xED, 0xAC],       'outd2')
check('OTI2R',      [0xED, 0xB4],       'oti2r')
check('OTD2R',      [0xED, 0xBC],       'otd2r')

# ---------------------------------------------------------------------------
section('eZ80 — ADL mode (24-bit)')
# ---------------------------------------------------------------------------
check('LD BC,24bit', [0x01, 0x56, 0x34, 0x12], 'ld BC,0x123456', adl=True)
check('JP 24bit',    [0xC3, 0x56, 0x34, 0x12], 'jp 0x123456',    adl=True)
check('CALL 24bit',  [0xCD, 0x56, 0x34, 0x12], 'call 0x123456',  adl=True)

# ---------------------------------------------------------------------------
section('eZ80 — Mode prefixes (.SIS/.LIS/.SIL/.LIL)')
# ---------------------------------------------------------------------------
check('.LIL CALL', [0x5B, 0xCD, 0x56, 0x34, 0x12], 'call.lil 0x123456')
check('.SIS LD BC',[0x40, 0x01, 0x34, 0x12],        'ld.sis BC,0x1234')

# ---------------------------------------------------------------------------
section('FLAGS helper')
# ---------------------------------------------------------------------------
from ez80dis import FLAGS
f = FLAGS(0x45)   # C | PV | Z
assert FLAGS.C  in f
assert FLAGS.PV in f
assert FLAGS.Z  in f
assert FLAGS.N  not in f
assert FLAGS.S  not in f
print(f'  OK    FLAGS(0x45) = {f.name}')

# ---------------------------------------------------------------------------
print(f'\n{"="*60}')
print(f'  {PASS} passed, {FAIL} failed')
print(f'{"="*60}')
sys.exit(1 if FAIL else 0)
