from gen_arc import gen_arc, boundary2
from visualization import movie
import numpy as np

b = boundary2((129, 129))
Phis_dbm, Phis_vis_dbm = gen_arc(b, method='ipcg', also=True, eta=3)
movie(np.sqrt(Phis_vis_dbm), iskwargs={'cmap': 'Blues'}, interval=5)