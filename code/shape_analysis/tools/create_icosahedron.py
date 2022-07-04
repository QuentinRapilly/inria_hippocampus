from meshzoo import icosa_sphere
import pyvista as pv
import numpy as np
import argparse


if __name__ == "__main__" : 
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--nb_div")
    parser.add_argument("-o", "--output")
    parser.add_argument("-s", "--space")

    args = parser.parse_args()
    output = args.output
    n = int(args.nb_div)
    points, edges = icosa_sphere(n)

    space = pv.read(args.space)
    x, X, y, Y, z, Z = space.GetBounds()
    bounds = np.array([[x,X],[y,Y],[z,Z]])
    gamma = np.max(bounds)/2
    middle = (bounds[:,0]+bounds[:,1])/2
    points = gamma*points + middle

    edges_modified = np.hstack((3*np.ones((edges.shape[0],1),dtype=int),edges)) 

    mesh = pv.PolyData(points, edges_modified)

    mesh.save(output)