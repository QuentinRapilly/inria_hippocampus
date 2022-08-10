import numpy as np


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
        for i in range(m):
            #print(data[i+2].split(" "))
            data_tab[i*d:(i+1)*d] = [float(x) for x in data[i+2].split(" ")[:-1]]
        vect_list.append(data_tab)
    
    alpha = np.vstack(vect_list)

    return alpha, (n, m, d)

def center_momenta(alpha):
    m = np.mean(alpha, axis = 0)
    print("Shape de alpha : {}, shape de la moyenne : {}".format(alpha.shape, m.shape))
    print("abs(moyenne(alpha))/moyenne(abs(alpha)) : {}".format(np.abs(m)/np.mean(np.abs(alpha),axis=0)))
    return alpha #- m

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


def expand_kernel(K, dimensions):

    n, m, d = dimensions

    # Expands the kernel matrix according to the dim of our data space (here 3) : 
    # block K_expanded(i,j) = K(i,j)Id_d
    K_expanded = np.zeros((m*d, m*d))
    
    for i in range(m):
        for j in range(m):
            K_expanded[i*d:(i+1)*d,j*d:(j+1)*d] = K[i,j]*np.eye(d)

    return K_expanded


def compute_eigen_vec(kpca_vec, momenta, keep_dim=0):
    V = momenta.T @ kpca_vec.T
    v_dim = V[:,keep_dim]
    v = np.vstack(np.array_split(v_dim, len(v_dim)/3))
    return v