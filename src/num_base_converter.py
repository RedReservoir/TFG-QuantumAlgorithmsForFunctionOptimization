def dec_to_bin(d, n):
    d = (d + 2**(n-1)) % 2**n - 2**(n-1)
    if d < 0: d = d + 2**n
    if d == 0: return "0" * n
    b = ""
    for _ in range(n):
        b = "1" + b if d%2 == 1 else "0" + b
        d = d//2
    return b

def bin_abs_to_dec(b):
    d = 0
    for c in b:
        d = 2 * d
        if c == "1": d = d + 1
    return d

def bin_ca2_to_dec(b):
    d = 0
    for c in b:
        d = 2 * d
        if c == "1": d = d + 1
    n = len(b)
    if d >= 2**(n-1): d = d - 2**n
    return d