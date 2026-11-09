"""Check yama's gap charges against Kececioglu-Zhang 1998 pessimistic (42)-(44).

1. Pointwise: yama's gop[16] table (read from the compiled binary) equals
   gap_open * Gamma_pess, with KZ's non-null bit = 1 - yama's dash flag.
2. Per step: on random paths, every interior step's open count from the KZ
   closed forms (42)-(44) as transcribed equals the pair-by-pair Gamma sum.
3. End to end: the score of the real yama's output equals the brute-force
   optimum over all paths under model Y (pessimistic Gamma everywhere, opens
   dropped on: I steps at row 0 or row M, C steps at col 1, D steps at col 0
   or col N). Also scores models that drop fewer opens, to show which drops
   are needed.
"""
import itertools, random, subprocess, sys

HOX70 = [[91, -114, -31, -123], [-114, 100, -125, -31],
         [-31, -125, 100, -114], [-123, -31, -114, 91]]
GO, GE = 400, 30
IDX = {c: n for n, c in enumerate("ACGT")}

def ss(a, b):
    if a == '-' and b == '-': return 0
    if a == '-' or b == '-': return -GE
    a, b = a.upper(), b.upper()
    if a in IDX and b in IDX: return HOX70[IDX[a]][IDX[b]]
    return -100

# KZ p.194 Gamma table, rows a1a2, cols b1b2, 1 = non-null; pessimistic.
G = {('00','00'):0,('00','01'):1,('00','10'):0,('00','11'):0,
     ('01','00'):1,('01','01'):0,('01','10'):1,('01','11'):0,
     ('10','00'):0,('10','01'):1,('10','10'):0,('10','11'):1,
     ('11','00'):0,('11','01'):0,('11','10'):1,('11','11'):0}
def gamma(a1, a2, b1, b2):
    return G[(f"{a1}{a2}", f"{b1}{b2}")]

def run(binary, cases):
    inp = []
    for A, B in cases:
        inp.append(f"{len(A[0])} {len(A)}"); inp += A
        inp.append(f"{len(B[0])} {len(B)}"); inp += B
    out = subprocess.run([binary], input="\n".join(inp) + "\n",
                         capture_output=True, text=True, check=True).stdout.split()
    res, p = [], 0
    for A, B in cases:
        m = int(out[p]); p += 1
        res.append(out[p:p+m]); p += m
    return res

def nn(c): return 0 if c == '-' else 1

def path_cols(A, B, ops):
    K, L = len(A[0]), len(B[0])
    i = j = 0; cols = []
    for op in ops:
        if op == 'C': i += 1; j += 1; cols.append((A[i-1], B[j-1], op, i, j))
        elif op == 'D': i += 1; cols.append((A[i-1], '-'*L, op, i, j))
        else: j += 1; cols.append(('-'*K, B[j-1], op, i, j))
    return cols

def score(A, B, ops, drop):
    M, N = len(A), len(B)
    K, L = len(A[0]), len(B[0])
    prevA, prevB = 'X'*K, 'X'*L      # KZ's artificial non-null column 0
    total = 0
    for a, b, op, i, j in path_cols(A, B, ops):
        total += sum(ss(x, y) for x in a for y in b)
        if not drop(op, i, j, M, N):
            opens = sum(gamma(nn(pa), nn(ca), nn(pb), nn(cb))
                        for pa, ca in zip(prevA, a) for pb, cb in zip(prevB, b))
            total -= GO * opens
        prevA, prevB = a, b
    return total

MODELS = {
    # yama as read: free row 0 and col 0, plus free I at row M, C at col 1, D at col N
    'Y':  lambda op, i, j, M, N: (op == 'I' and (i == 0 or i == M)) or
                                 (op == 'C' and j == 1) or
                                 (op == 'D' and (j == 0 or j == N)),
    # the claim as worded: (42)-(44) everywhere off the boundary, boundary free
    'Y0': lambda op, i, j, M, N: (op == 'I' and i == 0) or (op == 'D' and j == 0)
                                 or (i == 1 and j == 1 and op == 'C' ),
    # Y without one of its three interior drops, to show each one is needed
    'Y-noIrowM': lambda op, i, j, M, N: (op == 'I' and i == 0) or
                                 (op == 'C' and j == 1) or
                                 (op == 'D' and (j == 0 or j == N)),
    'Y-noCcol1': lambda op, i, j, M, N: (op == 'I' and (i == 0 or i == M)) or
                                 (op == 'C' and i == 1 and j == 1) or
                                 (op == 'D' and (j == 0 or j == N)),
    'Y-noDcolN': lambda op, i, j, M, N: (op == 'I' and (i == 0 or i == M)) or
                                 (op == 'C' and j == 1) or
                                 (op == 'D' and j == 0),
    # Y plus a symmetric drop of C-state opens at row 1: tests the asymmetry
    'Y+Crow1': lambda op, i, j, M, N: (op == 'I' and (i == 0 or i == M)) or
                                 (op == 'C' and (j == 1 or i == 1)) or
                                 (op == 'D' and (j == 0 or j == N)),
    # pure pessimistic, nothing free
    'P':  lambda op, i, j, M, N: False,
}

def all_paths(M, N):
    def rec(i, j):
        if i == M and j == N: yield (); return
        if i < M and j < N:
            for r in rec(i+1, j+1): yield ('C',) + r
        if i < M:
            for r in rec(i+1, j): yield ('D',) + r
        if j < N:
            for r in rec(i, j+1): yield ('I',) + r
    return list(rec(0, 0))

def ops_from_output(cols, K):
    return tuple('I' if set(c[:K]) == {'-'} else 'D' if set(c[K:]) == {'-'} else 'C'
                 for c in cols)

def rand_block(rows, length, rng):
    alpha = "ACGTACGTacgtN----"
    blk = []
    while len(blk) < length:
        c = "".join(rng.choice(alpha) for _ in range(rows))
        if set(c) != {'-'}: blk.append(c)
    return blk

# closed forms (42)-(44), pessimistic, as transcribed; f counts with KZ bits
def fcounts(blk, idx):
    """f1, f0, f00, f01, f10, f11 for column idx (1-based); column 0 non-null."""
    cur = [nn(c) for c in blk[idx-1]]
    prev = [1]*len(cur) if idx == 1 else [nn(c) for c in blk[idx-2]]
    f = {'1': sum(cur), '0': len(cur) - sum(cur)}
    for x in (0, 1):
        for y in (0, 1):
            f[f"{x}{y}"] = sum(1 for p, c in zip(prev, cur) if p == x and c == y)
    return f

def kz_opens(A, B, prev_op, op, i, j):
    k, l = len(A[0]), len(B[0])
    if op == 'I':      # KZ H(i,j), eq (42); A column i is the previous A column
        fa, fb = fcounts(A, i), fcounts(B, j)
        return {'I': k*fb['01'], 'D': k*fb['1'],
                'C': fa['1']*fb['1'] + fa['0']*fb['01']}[prev_op]
    if op == 'D':      # KZ V(i,j), eq (43)
        fa, fb = fcounts(A, i), fcounts(B, j)
        return {'I': l*fa['1'], 'D': l*fa['01'],
                'C': fa['1']*fb['1'] + fa['01']*fb['0']}[prev_op]
    fa, fb = fcounts(A, i), fcounts(B, j)   # KZ D(i,j), eq (44)
    return {'I': fa['1']*fb['0'] + fa['0']*fb['01'],
            'D': fa['0']*fb['1'] + fa['01']*fb['0'],
            'C': fa['1']*fb['10'] + fa['10']*fb['1'] + fa['00']*fb['01'] + fa['01']*fb['00']}[prev_op]

def main():
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
    ncase = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    for binary in sys.argv[3:]:
        gop = subprocess.run([binary, '-g'], capture_output=True, text=True).stdout.split()
        gop = list(map(int, gop[:16]))
        bad = 0
        for s, t, u, v in itertools.product((0, 1), repeat=4):
            g = gop[(s << 3) + (t << 2) + (u << 1) + v]
            k = GO * gamma(1-s, 1-u, 1-t, 1-v)
            bad += g != k
        name = binary.rsplit('/', 1)[-1]
        print(f"[1] {name}: gop[16] vs gap_open*Gamma_pess(1-s 1-u, 1-t 1-v): {16-bad}/16 equal")

    # [2] per-step closed forms vs pair-by-pair Gamma, interior steps i>=1, j>=1
    steps = mism = 0
    for _ in range(3000):
        K, L, M, N = (rng.randint(1, 4) for _ in range(4))
        A, B = rand_block(K, M, rng), rand_block(L, N, rng)
        ops = rng.choice(all_paths(M, N)) if M*N <= 16 else None
        if ops is None: continue
        cols = path_cols(A, B, ops)
        for t in range(1, len(cols)):
            a, b, op, i, j = cols[t]
            if i == 0 or j == 0: continue
            pa, pb, pop = cols[t-1][0], cols[t-1][1], cols[t-1][2]
            brute = sum(gamma(nn(x), nn(y), nn(w), nn(z))
                        for x, y in zip(pa, a) for w, z in zip(pb, b))
            steps += 1
            mism += brute != kz_opens(A, B, pop, op, i, j)
    print(f"[2] interior steps checked: {steps}, closed form != Gamma sum: {mism}")

    # [3] real yama vs brute-force optima
    cases = []
    for _ in range(ncase):
        K, L = rng.randint(1, 4), rng.randint(1, 4)
        M, N = rng.randint(1, 5), rng.randint(1, 5)
        cases.append((rand_block(K, M, rng), rand_block(L, N, rng)))
    for binary in sys.argv[3:]:
        outs = run(binary, cases)
        stats = {m: 0 for m in MODELS}
        for (A, B), cols in zip(cases, outs):
            ops = ops_from_output(cols, len(A[0]))
            paths = all_paths(len(A), len(B))
            for name, drop in MODELS.items():
                best = max(score(A, B, p, drop) for p in paths)
                stats[name] += score(A, B, ops, drop) == best
        print(f"[3] {binary.rsplit('/',1)[-1]}: {ncase} random cases, yama output optimal under "
              + ", ".join(f"{m}: {c}/{ncase}" for m, c in stats.items()))

main()
