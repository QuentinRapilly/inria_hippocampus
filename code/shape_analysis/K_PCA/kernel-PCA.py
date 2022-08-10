import argparse
import numpy as np
from os import listdir
from os.path import join

from kpca_tools import manage_momenta, manage_control_points, compute_kernel, expand_kernel, center_momenta


# Rappel des notations 
# alpha : momenta (n, m*d)
# points : control points (m, d)
# n : number of shapes
# d : number of dimensions
# m : number of control points
# K : kernel(m,m)
# K_expanded : (m*d, m*d) 
# M : (n*n) matrix containing scalar products between shapes


def compute_PCA(alpha, K, dimensions, exp_var=0.95, verbose=True):
    """
        Computes the Kernel PCA algorithm
    """
    n, m, d = dimensions

    if verbose : print("Shape alpha : {}".format(alpha.shape))

    # Expands the kernel matrix according to the dim of our data space (here 3) : 
    # block K_expanded(i,j) = K(i,j)Id_d
    K_expanded = expand_kernel(K, dimensions)
       

    if verbose : print("K_expanded shape : {}".format(K_expanded.shape))

    # Computes the matrix to diagonalize
    M = alpha @ K_expanded @ alpha.T
    if verbose : print("M shape : {}".format(M.shape))

    # Diagonalization process
    w, v = np.linalg.eig(M)
    w = np.real(w) #/n
    v = np.real(v)
    
    order = np.flip(np.argsort(w))
    sorted_vp = w[order]
    if verbose : print("Vp sorted : {}".format(sorted_vp))
    tot_variance = np.cumsum(sorted_vp)
    
    ind_var = np.argmax(tot_variance>exp_var*tot_variance[-1])

    sorted_v = [v[:,order[i]] for i in range(ind_var)]
    sorted_v = np.vstack(sorted_v)

    if verbose : print("Vect : {}".format(sorted_v))

    if verbose : print("Sorted_v : {}".format(sorted_v.shape))

    V = alpha.T @ sorted_v.T

    return sorted_vp, sorted_v

def kernel_PCA(data_files, control_points, std):
    alpha, dims = manage_momenta(data_files)

    centered_alpha = center_momenta(alpha)

    points = manage_control_points(control_points)

    K = compute_kernel(points, std)

    res = compute_PCA(centered_alpha, K, dims)

    return res

def normalize_vectors(eigen_val, eigen_vec):
    norm = np.linalg.norm(eigen_vec, axis = 0)

    return eigen_vec/(norm*np.sqrt(eigen_val))

def normalize_values(eigen_val):
    return eigen_val/np.sum(eigen_val)

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
    std = float(args.std)

    sorted_vp, sorted_v = kernel_PCA(data_files, control_points, std)

    print(sorted_v.shape)

    norm_v = normalize_vectors(sorted_vp, sorted_v)

    norm_vp = normalize_values(sorted_vp)

    print(norm_v.shape)

    np.savez(output, eigen_values = norm_vp, eigen_vectors= norm_v)

    
