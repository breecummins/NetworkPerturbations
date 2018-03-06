import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams.update({'font.size': 22})
from curve import Curve
import triplet_merge_trees as tmt
import sublevel_sets as ss

x = np.arange(-2.5,5.01,0.01)
y = 0.15*x**4 - 0.32*x**3 - 1.305*x**2 +0.27*x
np.random.seed(0)
eta = np.random.normal(0,0.25,x.shape)
z = y+eta
plt.plot(x,z,linewidth=2)
plt.plot(x,y,linewidth=1.25,color="red",zorder=10)
plt.savefig("noisy_curve.pdf",format = "pdf")

epsilons = [0.25,0.5,0.75,1.0,1.55, 2.33]

curve = Curve({ t : v for (t,v) in zip(x,z) })
births_only_merge_tree = tmt.births_only(curve.curve)

print("Noisy curve")
for eps in epsilons:
    time_ints = ss.minimal_time_ints(births_only_merge_tree,curve.curve,eps)
    print("The number of minima is {} at noise level {}.".format(len(time_ints),eps))
    print("Minimal time interval for x = 2.97: {}".format(time_ints[2.9699999999998834]))

curve = Curve({ t : v for (t,v) in zip(x,y) })
births_only_merge_tree = tmt.births_only(curve.curve)

print("Smooth curve")
for eps in epsilons:
    time_ints = ss.minimal_time_ints(births_only_merge_tree,curve.curve,eps)
    print("The number of minima is {} at noise level {}.".format(len(time_ints),eps))
    print("Minimal time interval for x = 3.00: {}".format(time_ints[2.9999999999998828]))


