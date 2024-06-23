import math
from collections import defaultdict

import e3nn_jax as e3nn

L_MAX = 14

def generate(l1, l2, l3, fp):
    cg = e3nn.clebsch_gordan(l1, l2, l3)
    fp.write(f"void tp_{l1}_{l2}_{l3}(const float* input1, const float* input2, float* output) {{\n")
    operations = defaultdict(list) # {out idx : [(c, input1 idx, input 2 idx)]}
    for m1 in range(-l1, l1 + 1):
        for m2 in range(-l2, l2 + 1):
            for m3 in range(-l3, l3 + 1):
                if cg[l1 + m1, l2 + m2, l3 + m3] != 0:
                    c = cg[l1 + m1, l2 + m2, l3 + m3] * math.sqrt(l3 * 2 + 1) # normalization
                    # fp.write(f"    output[{l3 + m3}] += {c} * input1[{l1 + m1}] * input2[{l2 + m2}];\n")
                    operations[l3 + m3].append((c, l1 + m1, l2 + m2))
                    
    # join operations by the output pointer they write to and write to out in
    # sequential order in memory
    for out_idx in sorted(operations.keys()):
        fp.write(f"    output[{out_idx}] = ")
        fp.write(" + ".join([f"{c} * input1[{idx1}] * input2[{idx2}]" for (c, idx1, idx2) in operations[out_idx]]))
        fp.write(";\n")
    fp.write("}\n\n")


with open("tp.h", "w") as hp:
    hp.write(
"""// autogenerated with
// python tp_codegen.py
#ifndef INCLUDED_TP_H
#define INCLUDED_TP_H

void tp(int l1, int l2, int l3, const float* input1, const float* input2, float* output);

#endif // ifndef INCLUDED_TP_H
""")

with open("tp.c", "w") as cp:
    cp.write(
'''// autogenerated with: 
// python tp_codegen.py
#include "tp.h"
#include "clebsch_gordan.h"
#include <stddef.h>

typedef void (*tp_ptr)(const float*, const float*, float*);

''')
    for l1 in range(L_MAX // 2 + 1):
        for l2 in range(L_MAX // 2 + 1):
            for l3 in range(abs(l1 - l2), l1 + l2 + 1):
                generate(l1, l2, l3, cp)

    cp.write(f"tp_ptr tps[{L_MAX // 2 + 1}][{L_MAX // 2 + 1}][{L_MAX + 1}] = {{\n")
    for l1 in range(L_MAX // 2 + 1):
        for l2 in range(L_MAX // 2 + 1):
            for l3 in range(abs(l1 - l2), l1 + l2 + 1):
                cp.write(f"    [{l1}][{l2}][{l3}] = tp_{l1}_{l2}_{l3},\n")
    cp.write("};\n")
    cp.write("""
void tp(int l1, int l2, int l3, const float* input1, const float* input2, float* output) {
    tps[l1][l2][l3](input1, input2, output);
}
""")

