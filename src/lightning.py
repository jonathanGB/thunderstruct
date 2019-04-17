from gen_arc import gen_arc, boundary2
from visualization import movie
import numpy as np
from time import time

b = boundary2((256, 256))
genArcTime = time()
Phis_dbm, Phis_vis_dbm = gen_arc(b, method='ipcg', also=True, eta=3)
print("Total time: {}".format(time() - genArcTime))
movie(np.sqrt(Phis_vis_dbm), iskwargs={'cmap': 'Blues'}, interval=5)