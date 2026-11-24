"""Minimal QR encoder (version 3, level L, byte mode) for the share dialog. Prints an SVG.
Usage: python3 tools/make_qr.py URL > qr.svg   (URL must be 53 bytes or fewer)"""
import sys

def rs_remainder(data, n):
    exp, log = [0] * 512, [0] * 256
    x = 1
    for i in range(255):
        exp[i] = x; log[x] = i
        x <<= 1
        if x & 0x100: x ^= 0x11D
    for i in range(255, 512): exp[i] = exp[i - 255]
    gen = [1]
    for i in range(n):
        nxt = [0] * (len(gen) + 1)
        for j, g in enumerate(gen):
            nxt[j] ^= g
            if g: nxt[j + 1] ^= exp[log[g] + i]
        gen = nxt
    rem = [0] * n
    for b in data:
        f = b ^ rem[0]
        rem = rem[1:] + [0]
        if f:
            for j in range(n):
                if gen[j + 1]: rem[j] ^= exp[log[gen[j + 1]] + log[f]]
    return rem

def matrix(text, mask=0):
    SIZE, DATA, ECC = 29, 55, 15
    raw = text.encode('utf-8')
    assert len(raw) <= 53, 'too long for version 3-L'
    bits = [0, 1, 0, 0] + [(len(raw) >> i) & 1 for i in range(7, -1, -1)]
    for b in raw: bits += [(b >> i) & 1 for i in range(7, -1, -1)]
    bits += [0] * min(4, DATA * 8 - len(bits))
    bits += [0] * (-len(bits) % 8)
    cw = [int(''.join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    pad = [0xEC, 0x11]
    while len(cw) < DATA: cw.append(pad[(len(cw) - len(bits) // 8) % 2])
    cw += rs_remainder(cw, ECC)
    m = [[0] * SIZE for _ in range(SIZE)]
    fn = [[False] * SIZE for _ in range(SIZE)]
    def put(x, y, v):
        if 0 <= x < SIZE and 0 <= y < SIZE: m[y][x] = 1 if v else 0; fn[y][x] = True
    for i in range(SIZE):
        put(6, i, i % 2 == 0); put(i, 6, i % 2 == 0)
    for cx, cy in ((3, 3), (SIZE - 4, 3), (3, SIZE - 4)):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                d = max(abs(dx), abs(dy)); put(cx + dx, cy + dy, d not in (2, 4))
    for dy in range(-2, 3):
        for dx in range(-2, 3): put(22 + dx, 22 + dy, max(abs(dx), abs(dy)) != 1)
    def fmt(mask):
        data = (1 << 3) | mask          # level L = 01
        rem = data
        for _ in range(10): rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        b = ((data << 10) | rem) ^ 0x5412
        bit = lambda i: (b >> i) & 1
        for i in range(6): put(8, i, bit(i))
        put(8, 7, bit(6)); put(8, 8, bit(7)); put(7, 8, bit(8))
        for i in range(9, 15): put(14 - i, 8, bit(i))
        for i in range(8): put(SIZE - 1 - i, 8, bit(i))
        for i in range(8, 15): put(8, SIZE - 15 + i, bit(i))
        put(8, SIZE - 8, 1)
    fmt(mask)
    i, right = 0, SIZE - 1
    while right >= 1:
        if right == 6: right = 5
        for vert in range(SIZE):
            for j in range(2):
                x = right - j
                y = SIZE - 1 - vert if ((right + 1) & 2) == 0 else vert
                if not fn[y][x]:
                    v = (cw[i >> 3] >> (7 - (i & 7))) & 1 if i < len(cw) * 8 else 0
                    m[y][x] = v ^ (1 if (x + y) % 2 == 0 else 0) if mask == 0 else v
                    i += 1
        right -= 2
    return m

def svg(m, quiet=4):
    n = len(m); d = ''
    for y, row in enumerate(m):
        x = 0
        while x < n:
            if row[x]:
                w = 1
                while x + w < n and row[x + w]: w += 1
                d += f'M{x + quiet} {y + quiet}h{w}v1h-{w}z'; x += w
            else: x += 1
    s = n + 2 * quiet
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" role="img" aria-label="QR code for the Anthem Wayfinder link" '
            f'shape-rendering="crispEdges"><rect width="{s}" height="{s}" fill="#fff"/><path fill="#000" d="{d}"/></svg>')

if __name__ == '__main__':
    sys.stdout.write(svg(matrix(sys.argv[1])))
