from lxml import etree
import subprocess as sub
import numpy as np
import sys
from tools import make_one_shape_only, julia_set

SEED = int(sys.argv[1])

RECORD_HISTORY = True  # saves the behavior movie

BODY_DIAMETER = 60  # in voxels
BODY_HEIGHT = 4  # in voxels

# body dims
bx, by, bz = (BODY_DIAMETER, BODY_DIAMETER, BODY_HEIGHT)

np.random.seed(SEED)

# get new voxcraft build
BUILD_DIR = "/home/slk6335/voxcraft-sim/build"
sub.call("cp {}/voxcraft-sim .".format(BUILD_DIR), shell=True)
sub.call("cp {}/vx3_node_worker .".format(BUILD_DIR), shell=True)

# create data folder if it doesn't already exist
sub.call("mkdir data{}".format(SEED), shell=True)
sub.call("cp base.vxa data{}/base.vxa".format(SEED), shell=True)

# clear old .vxd robot files from the data directory
sub.call("rm data{}/*.vxd".format(SEED), shell=True)

# delete old hist file
sub.call("rm a{}.hist".format(SEED), shell=True)

# remove old sim output.xml to save new stats
sub.call("rm output{}.xml".format(SEED), shell=True)


### fractal magic here ###
threshold = 25  # when to count the fractal as present
fractal = julia_set(c=.28 +.0081j, height=bx, width=by, max_iterations=256)
shape = make_one_shape_only(fractal > threshold)
##########################

# body
body = np.ones((bx, by, bz), dtype=np.int8)
for z in range(bz):
    body[:,:,z] = shape

# reformat data for voxcraft
body = np.swapaxes(body, 0,2)
body = body.reshape(bz, bx*by)

# phase offsets
phase = np.zeros((bx, by, bz))
for z in range(bz):
    phase[:,:,z] = 2*fractal/np.max(fractal)-1

# reformat phase for voxcraft
phase = np.swapaxes(phase, 0,2)
phase = phase.reshape(bz, bx*by)

# start vxd file
root = etree.Element("VXD")

if RECORD_HISTORY:
    # sub.call("rm a{0}_gen{1}.hist".format(seed, pop.gen), shell=True)
    history = etree.SubElement(root, "RecordHistory")
    history.set('replace', 'VXA.Simulator.RecordHistory')
    etree.SubElement(history, "RecordStepSize").text = '100'
    etree.SubElement(history, "RecordVoxel").text = '1'
    etree.SubElement(history, "RecordLink").text = '0'
    etree.SubElement(history, "RecordFixedVoxels").text = '1'
    etree.SubElement(history, "RecordCoMTraceOfEachVoxelGroupfOfThisMaterial").text = '0'  # draw CoM trace
    
structure = etree.SubElement(root, "Structure")
structure.set('replace', 'VXA.VXC.Structure')
structure.set('Compression', 'ASCII_READABLE')
etree.SubElement(structure, "X_Voxels").text = str(bx)
etree.SubElement(structure, "Y_Voxels").text = str(by)
etree.SubElement(structure, "Z_Voxels").text = str(bz)

data = etree.SubElement(structure, "Data")
for i in range(body.shape[0]):
    layer = etree.SubElement(data, "Layer")
    str_layer = "".join([str(c) for c in body[i]])  # the body doesn't have commas between the voxels
    layer.text = etree.CDATA(str_layer)

data = etree.SubElement(structure, "PhaseOffset")
for i in range(phase.shape[0]):
    layer = etree.SubElement(data, "Layer")
    str_layer = "".join([str(c) + ", " for c in phase[i]]) # other variables can be floats so they need commas
    layer.text = etree.CDATA(str_layer)

# save the vxd to data folder
with open('data'+str(SEED)+'/bot_0.vxd', 'wb') as vxd:
    vxd.write(etree.tostring(root))

# ok let's finally evaluate all the robots in the data directory

if RECORD_HISTORY:
    sub.call("./voxcraft-sim -i data{0} -o output{0}.xml -f > a{0}.hist".format(SEED), shell=True)
else:
    sub.call("./voxcraft-sim -i data{0} -o output{0}.xml".format(SEED), shell=True)
