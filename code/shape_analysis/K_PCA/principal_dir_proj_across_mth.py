import argparse
import numpy as np
from os import listdir
from os.path import join
import matplotlib.pyplot as plt
from ntpath import basename
from kpca_tools import center_momenta


from kpca_tools import manage_momenta, manage_control_points, compute_kernel, expand_kernel

MARKER_LIST = ["o", "v", "s", "*", "+"]

"""
def get_subject_id(filename):
    splitted = basename(filename).split("_")
    id = "{}_S_{}".format(splitted[-4],splitted[-2])

    return id


def compute_color_dictionnary(aging_file, group_id = "CN", verbose = False):

    age_dict = {}
    mini, maxi = 100, 0
    with open(aging_file, "r") as f:
        df = csv.DictReader(f, delimiter=";")
        for data in df: 
            if data.get("Group") == group_id and data.get("Subject") != "":
                crt_age = int(data["Age"])
                crt_sub = data["Subject"]
                if verbose : print("L'age de {} est : {}".format(crt_sub, crt_age))
                age_dict[crt_sub] = crt_age

                if crt_age<mini : mini = crt_age
                if crt_age>maxi : maxi = crt_age

    color_dict = {}

    colormap = cm.batlow

    for subject in age_dict:
        crt_float = (age_dict[subject]-mini)/(maxi-mini)
        color_dict[subject] = colormap(crt_float)

    return age_dict, color_dict """

def get_used_method(filename, methods):
    if methods == None:
        return "current"
    else :
        for method in methods:
            if filename.find(method) >= 0 : return method


def plot_proj(proj, dims_to_keep, idx_method, filenames, methods, output, verbose = True):

    dim0, dim1 = dims_to_keep[0], dims_to_keep[1]
    if verbose : print("Dim0 : {}".format(dim0))

    color_dict = {"dim_{}".format(dim0) : "b", "dim_{}".format(dim1) : "g", "mean" : "r"}
    colors_list = [color_dict[get_used_method(filename)] for filename in filenames]
    colors = np.array(colors_list)

    # Scatter 
    if methods == None :
        crt_method_idx = idx_method["current"]
        plt.scatter(x=proj[crt_method_idx,dim0], y=proj[crt_method_idx,dim1], c=colors[crt_method_idx], marker='o', label = "current")

    else :
        for i,method in enumerate(methods) :
            crt_method_idx = idx_method[method]
            marker = MARKER_LIST[i]
            plt.scatter(x=proj[crt_method_idx,dim0], y=proj[crt_method_idx,dim1], c=colors[crt_method_idx], marker=marker, label = method)
     

        """for subject in subject_dic:
            res = subject_dic[subject]
            tab = np.vstack(res)
            x, y = tab[:,dim0], tab[:,dim1]
            plt.plot(x, y, c=color_dict[subject], linestyle="--", linewidth=0.3)"""

    plt.legend()

    plt.savefig(output)

"""def analyze_variance(proj, idx_method, subject_dic, methods, output, verbose = True):
    std_method = {}
    if methods == None :
        crt_std = np.std(proj[idx_method["current"]], axis=0)
        std_method["current"] = crt_std
    else :
        for method in methods :
            crt_std = np.std(proj[idx_method[method]], axis=0)
            std_method[method] = crt_std
            if verbose : print("{} variance on each direction :\n{}".format(crt_std))

    by_subject_std = [np.std(np.vstack(subject_dic[subject]),axis=0) for subject in subject_dic]
    sub_std = np.vstack(by_subject_std)
    print(sub_std.shape)
    std_subject = np.mean(sub_std, axis=0)
    print("Subject variance :\n {}".format(std_subject))

    np.savez(output, var_method=std_method, var_subject=std_subject)"""

def compute_proj(momenta_files, control_points, eigen, std, dims_to_keep, output = "./output", methods=None, verbose = False):
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
    if methods == None :
        idx_method = {"current" : []}
    else :
        idx_method = {}
        for method in methods :
           idx_method[method] = []

    #subject_dic = {}

    for i, filename in enumerate(momenta_files):
        
        real_name = basename(filename)
        if verbose : print(real_name)
        
        method = get_used_method(real_name, methods)
        idx_method[method].append(i)

        #id = get_subject_id(real_name)

        """
        res = subject_dic.get(id)
        if res == None:
            subject_dic[id] = [proj[i]]
        else:
            res.append(proj[i])"""

    
    # To plot
    plot_output = join(output, "plot.png")
    plot_proj(proj, dims_to_keep, idx_method, momenta_files, methods, plot_output, verbose=verbose)

    # To analyze variance
    #var_output = join(output, "var.npz")
    #analyze_variance(proj, idx_method, subject_dic, methods, var_output)


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--momenta")
    parser.add_argument("-c","--control_points")
    parser.add_argument("-e", "--eigen")
    parser.add_argument("-s", "--std")
    parser.add_argument("-o", "--output")
    parser.add_argument("-d", "--dims")
    parser.add_argument("-M", "--methods", help="Methods' names used for this analysis (to process filenames)", default=None)


    args = parser.parse_args()
    momenta_dir = args.momenta

    dims_to_keep = [int(d) for d in args.dims.split(",")]

    momenta_files = [join(momenta_dir, filename) for filename in listdir(momenta_dir)]
    print("momenta_files")

    std = float(args.std)

    if args.methods == None:
        methods = None
        print("No method provided")
    else : 
        methods = [m for m in args.methods.split(",")]

    compute_proj(momenta_files, args.control_points, args.eigen, std, dims_to_keep, output = args.output, methods=methods)