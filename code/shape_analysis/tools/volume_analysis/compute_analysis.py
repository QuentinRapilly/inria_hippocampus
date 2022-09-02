from cProfile import label
import pyvista as pv 
import argparse
from os import listdir, mkdir
from os.path import join, isdir
from matplotlib import pyplot as plt

COLORS_LIST = ["b", "g", "r", "c", "m"]
MARKERS_LIST = ["v", "o", "s", "*"]
 
def process_name(name):
    if name.find("mean")>=0:
        return "mean", 0
    else :
        _, dim, _, std = name.split('_')
        std = int(std.split('.')[0])

        return "dim_{}".format(dim), std


def compute_volume(input_dir, output_f):
    ax_dict = {}

    with open(output_f, "w") as f:
        for filename in listdir(input_dir):
            mesh = pv.read(join(input_dir,filename))
            mesh.compute_cell_sizes()
            v = mesh.volume

            f.write("{} : {} mm3".format(filename, v))

            ax, std = process_name(filename)
            get = ax_dict.get(ax)
            if get == None :
                ax_dict[ax] = {"x":[std], "v":[v]}
            else :
                get["x"].append(std)
                get["v"].append(v)

    return ax_dict

    
def plot_volume(ax_dict, output_file):

    for i,ax_key in enumerate(ax_dict):
        ax = ax_dict.get(ax_key)
        plt.scatter(x=ax.get("x"), y=ax.get("v"), c=COLORS_LIST[i], marker=MARKERS_LIST[i], label=ax_key)
        
    plt.title("Volume evolution along main directions axis")
    plt.xlabel("Nb of std along axis")
    plt.ylabel("Volume (in mm3)")
    plt.legend()
    plt.savefig(output_file)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir")
    parser.add_argument("-o", "--output_dir")

    args = parser.parse_args()

    output_dir = args.output_dir
    if not isdir(output_dir):
        mkdir(output_dir)

    o_plot = join(output_dir, "volume.png")
    o_txt = join(output_dir, "volume.txt")

    ax_dict = compute_volume(args.input_dir, o_txt)
    plot_volume(ax_dict, o_plot)

