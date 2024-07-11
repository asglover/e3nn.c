# run with:
# ```
# python extra/benchmark_c_codegen.py > benchmark.c
# ```

import e3nn_jax as e3nn

from benchmark_python import L, channels, trials

print(
"""// autogenerated with:
// python extra/benchmark_c_codegen.py > benchmark.c
#include <stdio.h>
#include <time.h>

#include "e3nn.h"

int main(void) {
""")

for version in ["_v1", "_v2", "_v3"]:
    print(f'printf("e3nn.c{version.replace("_", " ")}\\n");')
    for lmax in range(1, L):
        irreps1 = e3nn.Irreps.spherical_harmonics(lmax)
        irreps2 = irreps1 * channels
        irrepso = e3nn.tensor_product(irreps1, irreps2)
        print(f'''
        {{
            Irreps* irreps1 = irreps_create("{irreps1}");
            Irreps* irreps2 = irreps_create("{irreps2}");
            Irreps* irrepso = irreps_create("{irrepso}");
            float input1[{irreps1.dim}] = {{ 0 }};
            float input2[{irreps2.dim}] = {{ 0 }};
            float output[{irrepso.dim}] = {{ 0 }};

            // do once to build Clebsch-Gordan cache if necessary
            tensor_product{version}(irreps1, input1,
                                    irreps2, input2,
                                    irrepso, output);

            clock_t start = clock(); 
            for (int trial = 0; trial < {trials}; trial++) {{
                tensor_product{version}(irreps1, input1,
                                        irreps2, input2,
                                        irrepso, output);
            }}
            float elapsed = ((float) clock() - start) / CLOCKS_PER_SEC; 
            printf("{lmax}, %f\\n", elapsed); 

            irreps_free(irreps1);
            irreps_free(irreps2);
            irreps_free(irrepso);
        }}
    ''')

print("""
    return 0;
}
""")