from gen_arc import gen_arc, boundary2
from visualization import movie
import numpy as np

b = boundary2((128,128))
Phis_dbm, Phis_vis_dbm = gen_arc(b, method='ipcg', also=True, eta=3)
movie(np.sqrt(abs(Phis_vis_dbm)), iskwargs={'cmap': 'Blues'}, interval=5)
