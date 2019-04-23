from gen_arc import gen_arc, boundary2, pcg, datdot, matmul
from visualization import movie
import numpy as np
from time import time

b = boundary2((100, 100))
print("b: {}".format(b.shape))

now = time()
Phis_dbm, Phis_vis_dbm = gen_arc(b, method='ipcg', also=True, eta=3)
total = time() - now
print("pcg @: {}s ({}%)\npcg.dot: {}s ({}%)\npcg.get_z: {}s ({}%)\n----------------\ngen_arc: {}"
  .format(pcg.at, pcg.at/total*100, pcg.dot, pcg.dot/total*100, pcg.get_z, pcg.get_z/total*100, total))

print(np.array(datdot.restimes).mean())
print(np.array(datdot.res2times).mean())

print("Dot vec time: {}s ({}%) - {} times\nDot mat time: {}s ({}%) - {} times".format(datdot.vectime, datdot.vectime/total*100, datdot.veccount, datdot.mattime, datdot.mattime/total*100, datdot.matcount))
print("Mat mul time: {}s ({}%) - {} times\n".format(matmul.mattime, matmul.mattime/total * 100, matmul.matcount))
np_time = np.array(matmul.restimes).sum()
go_time = np.array(matmul.res2times).sum()

print("Total numpy time: {}s vs. Go, Parallel implementation: {}s".format(np_time, go_time))


#movie(np.sqrt(Phis_vis_dbm), iskwargs={'cmap': 'Blues'}, interval=5)