import fmmgen

order = 10
source_order = 1
cse = True
atomic = True
precision='double'
fmmgen.generate_code(order, "operators",
                     precision=precision,
                     CSE=cse,
                     generate_cython_wrapper=False,
                     potential=False,
                     field=True,
                     include_dir="include",
                     src_dir="src",
                     source_order=source_order,
                     atomic=atomic)