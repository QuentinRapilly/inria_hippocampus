import argparse
import numpy as np
from os import listdir
from os.path import join


# Rappel des notations 
# alpha : momenta (n, m*d)
# points : control points (m, d)
# n : number of shapes
# d : number of dimensions
# m : number of control points
# K : kernel(m,m)
# K_expanded : (m*d, m*d) 
# M : (n*n) matrix containing scalar products between shapes

### READING ###

## Reading of the momenta files
def manage_momenta(data_files):
    vect_list = list()
    n = len(data_files)
    for filename in data_files :
        with open(filename,"r") as f:
            data = f.readlines()
        _, m, d = [int(x) for x in data[0].split(" ")]

        data_tab = np.zeros((m*d))
        for i in range(n):
            data_tab[i*d:(i+1)*d] = [float(x) for x in data[i+2].split(" ")]
        vect_list.append(data_tab)
    
    alpha = np.vstack(vect_list)

    return alpha, (n, m, d)

## Reading the control points file
def manage_control_points(control_points_file):
    with open(control_points_file, "r") as f:
        lines = f.readlines()
    points = np.array([[float(x) for x in line.split(" ")] for line in lines])
    
    return points

### EXPLOITING ###
def compute_kernel(points, std):
    """
        Computes the value of K(x_i, x_j) for every pair of control points
    """
    pairwise_dist = np.linalg.norm(points[:,None,:] - points[None,:,:], axis=-1)
    in_exp = -np.power(pairwise_dist, 2)/std**2
    K = np.exp(in_exp)

    return K

def compute_PCA(alpha, K, dimensions, exp_var=0.9):
    """
        Computes the Kernel PCA algorithm
    """
    n, m, d = dimensions

    # Expands the kernel matrix according to the dim of our data space (here 3) : 
    # block K_expanded(i,j) = K(i,j)Id_d
    K_expanded = np.zeros((m*d, m*d))

    for i in range(m):
        for j in range(m):
            K_expanded[i*d:(i+1)*d,j*d:(j+1)*d] = K[i,j]*np.eye(d)
    
    # Computes the matrix to diagonalize
    M = alpha @ K_expanded @ alpha.T

    # Diagonalization process
    w, v = np.linalg.eig(M)
    vp = w/np.sum(w)
    order = np.flip(np.argsort(vp))
    sorted_vp = vp[order]
    tot_variance = np.cumsum(sorted_vp)

    ind_var = np.argmax(tot_variance>exp_var)

    sorted_v = [v[:,order[i]] for i in range(ind_var)]
    sorted_v = np.vstack(sorted_v)

    V = alpha.T @ sorted_v

    return sorted_vp, sorted_v

def kernel_PCA(data_files, control_points, std):
    alpha, dims = manage_momenta(data_files)
    points = manage_control_points(control_points)

    K = compute_kernel(points, std)

    res = compute_PCA(alpha, K, dims)

    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Directory where the momentum are stored")
    parser.add_argument("-o", "--output", help="Npz file where the results of the K-PCA are stored")
    parser.add_argument("-c", "--control_points", help="File containing the control points")
    parser.add_argument("-s", "--std", help="Value of std for the deformation kernel")

    args = parser.parse_args()
    input = args.input
    output = args.output
    data_files = [join(input, filename) for filename in listdir(input)]

    control_points = args.control_points
    std = args.std

    sorted_vp, sorted_v = kernel_PCA(data_files, control_points, std)

    np.savez(output, eigen_values = sorted_vp, eigen_vectors= sorted_v)

    