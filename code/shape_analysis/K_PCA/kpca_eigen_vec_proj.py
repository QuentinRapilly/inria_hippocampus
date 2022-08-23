import argparse
from re import sub
from typing import Dict
import numpy as np
from os import listdir
from os.path import join
import matplotlib.pyplot as plt
from ntpath import basename
from kpca_tools import center_momenta

from cmcrameri import cm
import csv

from kpca_tools import manage_momenta, manage_control_points, compute_kernel, expand_kernel


def get_subject_id(filename):
    splitted = filename.split("_")
    id = "{}_S_{}".format(splitted[-4],splitted[-2])

    return id


def compute_color_dictionnary(aging_file):

    age_dict = {}
    mini, maxi = 100, 0
    with open(aging_file, "r") as f:
        df = csv.DictReader(f)
        for data in df: 
            if data.get("Group") == "CN":
                crt_age = int(data["Age"])
                age_dict[data["Subject"]] = crt_age

                if crt_age<mini : mini = crt_age
                if crt_age>maxi : maxi = crt_age

    color_dict = {}

    colormap = cm.batlow

    for subject in age_dict:
        crt_float = (age_dict[subject]-mini)/(maxi-mini)
        color_dict[subject] = colormap(crt_float)

    return age_dict, color_dict

def get_used_method(filename):
    if filename.find("ashs")>=0: return "ashs"
    if filename.find("fsl")>=0: return "fsl"
    if filename.find("g_truth")>=0: return "g_truth"


def plot_proj(proj, dims_to_keep, idx_method, subject_dic, filenames, output, aging_file, verbose = True):

    dim0, dim1 = dims_to_keep[0], dims_to_keep[1]
    if verbose : print("Dim0 : {}".format(dim0))

    _, color_dict = compute_color_dictionnary(aging_file)
    print(color_dict)
    colors_list = [color_dict[get_subject_id(filename)] for filename in filenames]


    colors = np.array(colors_list)

    ashs_idx, fsl_idx, g_truth_idx = idx_method["ashs"], idx_method["fsl"], idx_method["g_truth"]

    # Scatter pour ASHS
    if verbose :
        print("x : {}\ny : {}\ncolors:{}".format(x[ashs_idx], y[ashs_idx], colors[ashs_idx]))
    plt.scatter(x=proj[ashs_idx,dim0], y=proj[ashs_idx,dim1], c=colors[ashs_idx], marker='o', label = "ASHS")
    # Scatter pour FSL
    plt.scatter(x=proj[fsl_idx,dim0], y=proj[fsl_idx,dim1], c=colors[fsl_idx], marker='v', label = "FSL")
    # Scatter pour G_TRUTH
    plt.scatter(x=proj[g_truth_idx,dim0], y=proj[g_truth_idx,dim1], c=colors[g_truth_idx], marker='s', label = "G_truth")        

    for subject in subject_dic:
        res = subject_dic[subject]
        tab = np.vstack(res)
        x, y = tab[:,dim0], tab[:,dim1]
        plt.plot(x, y, c=color_dict[subject], linestyle="--", linewidth=0.3)

    plt.legend()

    plt.savefig(output)

def analyze_variance(proj, idx_method, subject_dic, output):
    ashs_std = np.std(proj[idx_method["ashs"]], axis=0)
    print("ASHS variance on each main direction :\n {}".format(ashs_std))
    fsl_std = np.std(proj[idx_method["fsl"]], axis=0)
    print("FSL variance on each main direction :\n {}".format(fsl_std))
    g_truth_std = np.std(proj[idx_method["g_truth"]], axis=0)
    print("G_truth variance on each main direction :\n {}".format(g_truth_std))

    std_method = {"ashs":ashs_std, "fsl":fsl_std, "g_truth":g_truth_std}

    by_subject_std = [np.std(np.vstack(subject_dic[subject]),axis=0) for subject in subject_dic]
    sub_std = np.vstack(by_subject_std)
    print(sub_std.shape)
    std_subject = np.mean(sub_std, axis=0)
    print("Subject variance :\n {}".format(std_subject))

    np.savez(output, var_method=std_method, var_subject=std_subject)

def compute_proj(momenta_files, control_points, eigen, std, dims_to_keep, output = "./output", aging_file = None, verbose = False):
    eigen_dic = np.load(eigen)
    eigen_vectors = eigen_dic["eigen_vectors"]

    alpha, dimensions = manage_momenta(momenta_files)

    points = manage_control_points(control_points)

    K = compute_kernel(points, std)

    K_expanded = expand_kernel(K, dimensions)

    c_alpha = center_momenta(alpha, K_expanded)

    n, m, d = dimensions

    M = c_alpha @ K_expanded @ c_alpha.T

    print("Shape de M : {}\nShape de eigen_vectors : {}".format(M.shape, eigen_vectors.shape))

    proj = M @ eigen_vectors.T


    # Tools for the following steps :

    idx_method = {"ashs":[], "fsl":[], "g_truth":[]}

    subject_dic = {}

    for i, filename in enumerate(momenta_files):
        
        real_name = basename(filename)
        if verbose : print(real_name)
        
        method = get_used_method(real_name)
        idx_method[method].append(i)

        id = get_subject_id(real_name)

        res = subject_dic.get(id)
        if res == None:
            subject_dic[id] = [proj[i]]
        else:
            res.append(proj[i])

    
    # To plot
    plot_output = join(output, "plot.png")
    plot_proj(proj, dims_to_keep, idx_method, subject_dic, momenta_files, plot_output, aging_file, verbose=verbose)

    # To analyze variance
    var_output = join(output, "var.npz")
    analyze_variance(proj, idx_method, subject_dic, var_output)






if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--momenta")
    parser.add_argument("-c","--control_points")
    parser.add_argument("-e", "--eigen")
    parser.add_argument("-s", "--std")
    parser.add_argument("-o", "--output")
    parser.add_argument("-d", "--dims")
    parser.add_argument("-a", "--age", help="Csv containing subjects' age")


    args = parser.parse_args()
    momenta_dir = args.momenta

    dims_to_keep = [int(d) for d in args.dims.split(",")]

    momenta_files = [join(momenta_dir, filename) for filename in listdir(momenta_dir)]

    std = float(args.std)

    compute_proj(momenta_files, args.control_points, args.eigen, std, dims_to_keep, output = args.output, aging_file=args.age)