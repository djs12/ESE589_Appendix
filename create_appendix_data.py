#!/usr/bin/env python2

"""
This application loads .mat appendix data (if not already done), converts to numpy format and writes to a new directory. The appendix numpy data is then converted to an octree format and written to a new directory.

Important to note: the .mat data is assumed to be in matlab version 7 format. Scipy will throw errors as it can't handle conversion with the latest matlab v7.3
"""

################################################################################
# Imports
################################################################################

import numpy as np
import os
from glob import glob
import scipy.io
import sys
import time

################################################################################
# Load .mat data and convert to npy data if appendix numpy directory not found
################################################################################

#This section assumes the .mat files are v7 (not v7.3!)
numpy_directory = "./appendix_numpy_tensors"
if not os.path.isdir(numpy_directory):
    os.mkdir(numpy_directory)
    #Personal Path to appendix .mat directory (Point root to where data is)
    #Edit this path for your scenario
    root = "/home/dan/Engineering/Class_by_Semester/Spring2019/Biomedical_Imaging/Project/Data/ESE589_Appendix_Project"
    #Container to store paths to all .mat files
    mat_paths = []
    for dirs, subdirs, files in os.walk(root):
        mat_paths.extend(glob(os.path.join(dirs, '*.mat')))
    mat_paths.sort()
    #Move into the newly created directory to begin saving data
    os.chdir(numpy_directory)
    #Loop through paths to every .mat file and write to new npy files
    for path in mat_paths:
        if ( path.find('uint8')  != -1):
            mat = scipy.io.loadmat(path)
            mat_as_numpy = np.array(mat['label_num'])
            filename = path.split("/")[-1].replace(".mat","")
            print("Saving " + filename)
            np.save(filename, mat_as_numpy)
        else:
            mat = scipy.io.loadmat(path)
            mat_as_numpy = np.array(mat['images'])
            filename = path.split("/")[-1].replace(".mat","")
            print("Saving " + filename)
            np.save(filename, mat_as_numpy)
    os.chdir("../")

################################################################################
# Convert appendix numpy data to octree format
################################################################################

sys.path.append('../py/')
sys.path.append('../example/00_create_data/')
import pyoctnet
import vis

#Again, check to see if the directory already exists. Otherwise generate the octrees
oc_directory ="./appendix_octrees"
if not os.path.isdir(oc_directory):
    os.mkdir(oc_directory)
    os.chdir(oc_directory)
    root = "../" + numpy_directory

    for dirs, subdirs, files in os.walk(root):
        files_left = len(files)
        for file in files:
            dense = np.load(root + "/" + file)
            print("Creating " + file + " as an octree!")
            t = time.time()
            oc_grid = pyoctnet.Octree.create_from_dense(np.ascontiguousarray(dense[np.newaxis], dtype=np.float32))
            print("Creation took %f[s]" % (time.time() - t))
            print("Saving result to a file")
            oc_grid.write_bin(file.split(".")[0] + ".oc")
            files_left = files_left - 1
            print("Done! " + str(files_left) + " more octrees to go!")
