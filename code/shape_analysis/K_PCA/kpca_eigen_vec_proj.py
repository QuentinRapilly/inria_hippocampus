import argparse
from matplotlib.lines import _LineStyle
import numpy as np
from os import listdir
from os.path import join
import matplotlib.pyplot as plt
from ntpath import basename

from kpca_tools import manage_momenta, manage_control_points, compute_kernel, expand_kernel

COLORS = {"ashs":"blue", "fsl":"res", "g_truth":"green"}

def get_subject_id(filename):
    splitted = filename.split("_")
    id = splitted[-4]+splitted[-2]

    return id

def get_subject_color(filename):
    id = get_subject_id(filename)
    r,g,b = (int(id[:3])/140)*0.6+0.4, (int(id[3:5])/100)*0.6+0.4, (int(id[5:])/100)*0.6+0.4

    return np.array([r,g,b])

def get_used_method(filename):
    if filename.find("ashs")>=0: return "ashs"
    if filename.find("fsl")>=0: return "fsl"
    if filename.find("g_truth")>=0: return "g_truth"


def compute_proj(momenta_files, control_points, eigen, std, dims_to_keep, output = "out.png", verbose = False):
    eigen_dic = np.load(eigen)
    eigen_vectors = eigen_dic["eigen_vectors"]

    alpha, dimensions = manage_momenta(momenta_files)

    n, m, d = dimensions

    points = manage_control_points(control_points)

    K = compute_kernel(points, std)

    K_expanded = expand_kernel(K, dimensions)

    M = alpha @ K_expanded @ alpha.T

    proj = M @ eigen_vectors[dims_to_keep].T

    x = proj[:,0]
    y = proj[:,1]

    ## METHOD DE PRINT 1
    """
    colors_list = list()

    ashs_idx, fsl_idx, g_truth_idx = [], [], []

    for i, filename in enumerate(momenta_files):
        
        real_name = basename(filename)
        if verbose : print(real_name)

        if real_name.find("ashs")>=0:
            ashs_idx.append(i)
        elif real_name.find("fsl")>=0:
            fsl_idx.append(i)
        elif real_name.find("g_truth")>=0:
            g_truth_idx.append(i)

        colors_list.append(get_subject_color(real_name))

    colors = np.array(colors_list)

    if verbose: print("ashs idx : {}".format(ashs_idx))


    # Scatter pour ASHS
    if verbose :
        print("x : {}\ny : {}\ncolors:{}".format(x[ashs_idx], y[ashs_idx], colors[ashs_idx]))
    plt.scatter(x=x[ashs_idx], y=y[ashs_idx], c=colors[ashs_idx], marker='o')
    # Scatter pour FSL
    plt.scatter(x=x[fsl_idx], y=y[fsl_idx], c=colors[fsl_idx], marker='v')
    # Scatter pour G_TRUTH
    plt.scatter(x=x[g_truth_idx], y=y[g_truth_idx], c=colors[g_truth_idx], marker='+')

    """

    ## FIN DE LA METHODE DE PRINT 1

    ## METHODE DE PRINT 2

    print_dic = {}

    for i,filename in enumerate(momenta_files) :
        real_name = basename(filename)
        id = get_subject_id(real_name)
        method = get_used_method(real_name)

        res = print_dic.get(id)
        if res == None:
            print_dic[id] = {"x":[x[i]], "y":[y[i]], "c":[COLORS[method]], "linestyle":"--"}
        else:
            res["x"].append(x[i])
            res["y"].append(y[i])
            res["c"].append(COLORS[method])

    for key in print_dic:
        plt.plot("x", "y", color="c", linestyle="linestyle", data=print_dic[key])

    plt.savefig(output)







if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--momenta")
    parser.add_argument("-c","--control_points")
    parser.add_argument("-e", "--eigen")
    parser.add_argument("-s", "--std")
    parser.add_argument("-o", "--output")
    parser.add_argument("-d", "--dims")


    args = parser.parse_args()
    momenta_dir = args.momenta

    dims_to_keep = [int(d) for d in args.dims.split(",")]

    momenta_files = [join(momenta_dir, filename) for filename in listdir(momenta_dir)]

    std = float(args.std)

    compute_proj(momenta_files, args.control_points, args.eigen, std, dims_to_keep, output = args.output)