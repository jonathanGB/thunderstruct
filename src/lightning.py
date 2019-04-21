from gen_arc import gen_arc, boundary2, pcg, datdot
from visualization import movie
import numpy as np
from time import time

b = boundary2((64, 64))
print("b: {}".format(b.shape))

now = time()
Phis_dbm, Phis_vis_dbm = gen_arc(b, method='ipcg', also=True, eta=3)
total = time() - now
print("pcg @: {}s ({}%)\npcg.dot: {}s ({}%)\npcg.get_z: {}s ({}%)\n----------------\ngen_arc: {}"
  .format(pcg.at, pcg.at/total*100, pcg.dot, pcg.dot/total*100, pcg.get_z, pcg.get_z/total*100, total))

print("Dot vec time: {}s ({}%) - {} times\nDot mat time: {}s ({}%) - {} times".format(datdot.vectime, datdot.vectime/total*100, datdot.veccount, datdot.mattime, datdot.mattime/total*100, datdot.matcount))
# movie(np.sqrt(Phis_vis_dbm), iskwargs={'cmap': 'Blues'}, interval=5)