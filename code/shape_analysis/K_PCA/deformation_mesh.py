import pyvista as pv
from sklearn.neighbors import NearestNeighbors
import numpy as np
from os import listdir
from os.path import join

import argparse

from kpca_tools import manage_control_points, manage_momenta

## Read data

def compute_eigen_vec_norm(kpca_v, momenta, keep_dim=0):
    V = momenta.T @ kpca_v.T
    #print("shape de V : {}, shape de V['keepp_dim'] : {}".format(V.shape, V[keep_dim].shape))
    v_dim = V[:,keep_dim]
    v = np.vstack(np.array_split(v_dim, len(v_dim)/3))
    v_norm = np.linalg.norm(v, 2, 1)
    return v_norm


## Process data


def create_tree(control_points, k=3):
    #print("Control points shape : {}".format(control_points.shape))
    knn = NearestNeighbors(n_neighbors=k, algorithm="auto").fit(control_points)
    return knn


def create_display_mesh(mesh, control_points, momenta, v_norm, output):
    points = mesh.points

    print("Creating tree")
    tree = create_tree(control_points)

    print("Finding k-nn")
    dist, idx = tree.kneighbors(points)

    #print("Shape dist : {}, v_norm : {}".format(dist.shape, v_norm.shape))

    field = np.array([np.sum(dist[i]*v_norm[idx[i]])/np.sum(dist[i]) for i in range(len(points))])

    m, M = np.min(field), np.max(field)
    #field = (field - m)/(M-m)

    mesh.point_data["deformation"] = field

    mesh.save(output)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--control_points")
    parser.add_argument("-v", "--vtk", help="Vtk mean shape")
    parser.add_argument("-m", "--momenta")
    parser.add_argument("-o", "--output")
    parser.add_argument("-k", "--kpca")
    parser.add_argument("-d", "--dimension")

    args = parser.parse_args()

    control_points = manage_control_points(args.control_points)

    momenta_dir = args.momenta
    momenta_files = [join(momenta_dir, filename) for filename in listdir(momenta_dir)]
    momenta, dims = manage_momenta(momenta_files)

    mesh = pv.read(args.vtk)

    kpca_v = np.load(args.kpca)["eigen_vectors"]
    keep_dim = int(args.dimension)
    v_norm = compute_eigen_vec_norm(kpca_v, momenta, keep_dim)

    create_display_mesh(mesh, control_points, momenta, v_norm, args.output)