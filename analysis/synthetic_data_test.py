import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams.update({'font.size': 22})
from queries.patternmatch.curve import Curve
import queries.patternmatch.posets as posets

x = np.arange(-2.5,5,0.01)
y = -0.25*x**4 + 1.33*x**3 + 0.5*x**2 - 4.0*x
np.random.seed(0)
# eps = np.random.normal(0,0.25,x.shape)
# y += eps

curve = Curve({ str(t) : v for (t,v) in zip(x,y) })
for p in posets.main({"curve":curve},[0.025]):
    print(p)

plt.plot(x,y,linewidth=2)
plt.show()







