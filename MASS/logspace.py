import numpy as np
l_space = sorted(list(set(np.array(np.round(np.logspace(np.log10(1),np.log10(32e3),num=118)),dtype=np.int32))))
assert len(l_space) == 101
with open('logspace_1_32k_101.txt', 'w') as f:
    for e in l_space:
        f.write('{:05d}\n'.format(e))
