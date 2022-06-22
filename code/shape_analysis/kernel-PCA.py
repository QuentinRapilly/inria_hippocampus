import argparse
import numpy as np
from os import listdir
from os.path import join
from scipy.spatial import 


### READING ###

## Reading of the momenta files
def manage_momenta(data_files):
    vect_list = list()
    for filename in data_files :
        with open(filename,"r") as f:
            data = f.readlines()
        _, n, p = [int(x) for x in data[0].split(" ")]

        data_tab = np.zeros((n*p))
        for i in range(n):
            data_tab[i*p:(i+1)*p] = [float(x) for x in data[i+2].split(" ")]
        vect_list.append(data_tab)
    
    vect = np.vstack(vect_list)

    return vect, n*p

## Reading the control points file
def manage_control_points(control_points_file):
    with open(control_points_file, "r") as f:
        lines = f.readlines()
    points = np.array([[float(x) for x in line.split(" ")] for line in lines])
    
    return points

### EXPLOITING ###
def compute_kernel(points, std):
    pairwise_dist = np.linalg.norm(points[:,None,:] - points[None,:,:], axis=-1)
    in_exp = -np.power(pairwise_dist, 2)/std**2
    kernel = np.exp(in_exp)

    return kernel

def compute_PCA(vect, kernel):
    l = vect.shape[0]
    C = (vect.T @ vect)/l

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Directory where the momentum are stored")


    args = parser.parse_args()
    input = args.input
    data_files = [join(input, filename) for filename in listdir(input)]


    