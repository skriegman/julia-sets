from lxml import etree
import subprocess as sub
import numpy as np
import sys
from tools import make_one_shape_only, julia_set

HASH = str(sys.argv[1])

A = float(sys.argv[2])  # .28
B = float(sys.argv[3])  # .0081

THRESHOLD = int(sys.argv[4])  # 25

RECORD_HISTORY = False  # saves the behavior movie

BODY_DIAMETER = 60  # in voxels
BODY_THICKNESS = 8

bx, by, bz = (BODY_DIAMETER, BODY_THICKNESS, BODY_DIAMETER)

# np.random.seed(SEED)

# get new voxcraft build
BUILD_DIR = "/home/slk6335/voxcraft-sim/build"
sub.call("cp {}/voxcraft-sim .".format(BUILD_DIR), shell=True)
sub.call("cp {}/vx3_node_worker .".format(BUILD_DIR), shell=True)

# create data folder if it doesn't already exist
sub.call("mkdir data{}".format(HASH), shell=True)
sub.call("cp base.vxa data{}/base.vxa".format(HASH), shell=True)

# clear old .vxd robot files from the data directory
sub.call("rm data{}/*.vxd".format(HASH), shell=True)

# delete old hist file
sub.call("rm a{}.hist".format(HASH), shell=True)

# remove old sim output.xml to save new stats
sub.call("rm output{}.xml".format(HASH), shell=True)


### fractal magic here ###
fractal = julia_set(c=A + B*1j, height=bx, width=bz, max_iterations=256)
shape = make_one_shape_only(fractal > THRESHOLD)
##########################

body = np.zeros((bx, by, bz), dtype=np.int8)  # morphology
phase = np.zeros((bx, by, bz))  # phase offsets

for thic in range(-by//2, by//2, 1):
    # body[:,:,bz//2+thic] = shape
    # phase[:,:,bz//2+thic] = 2*fractal/np.max(fractal)-1
    body[:,by//2+thic,:] = shape
    phase[:,by//2+thic,:] = 2*fractal/np.max(fractal)-1

# remove zero padding
xs,ys,zs = np.where(body!=0) 
body = body[min(xs):max(xs)+1,min(ys):max(ys)+1,min(zs):max(zs)+1]
phase = phase[min(xs):max(xs)+1,min(ys):max(ys)+1,min(zs):max(zs)+1]
bx, by, bz = body.shape

# reformat data for voxcraft
body = np.swapaxes(body, 0,2)
body = body.reshape(bz, bx*by)

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
with open('data'+str(HASH)+'/bot_0.vxd', 'wb') as vxd:
    vxd.write(etree.tostring(root))

# ok let's finally evaluate all the robots in the data directory

if RECORD_HISTORY:
    sub.call("./voxcraft-sim -i data{0} -o output{0}.xml -f > a{0}.hist".format(HASH), shell=True)
else:
    sub.call("./voxcraft-sim -i data{0} -o output{0}.xml".format(HASH), shell=True)
