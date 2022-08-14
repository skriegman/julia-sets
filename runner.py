import numpy as np
import subprocess as sub
from lxml import etree
import random
import cma


def cost_function(params):

    A,B,T = params

    H = format(random.getrandbits(32), 'x')

    sub.check_call("~/miniconda3/bin/python single_robot.py {0} {1} {2} {3}".format(H, A, B, int(T)), shell=True)
    
    root = etree.parse("output{0}.xml".format(H)).getroot()
    fitness = np.abs(float(root.findall("detail/bot_0/fitness_score")[0].text))

    print("****** The fitness is: {} ******".format(fitness))

    return -fitness


opts = cma.CMAOptions()
opts.set("bounds", [[-2, -2, 0], [2, 2, 100]])
cma.fmin(cost_function, [0.1,0.001,25], 0.001, opts)

