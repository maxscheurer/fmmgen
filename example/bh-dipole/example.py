import fmmgen

order = 8
cse = True

fmmgen.generate_code(order, "operators", CSE=cse, generate_cython_wrapper=False,
                     include_dir="include", src_dir="src")
