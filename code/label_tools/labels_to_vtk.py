import argparse
from os import popen, listdir, mkdir, remove
from os.path import join

def create_binary_file(input_file, output_file, upper, lower):
    cmd = "animaThrImage -u {} -t {} -i {} -o {}".format(upper, lower, input_file, output_file)
    popen(cmd)

def create_vtk(input_file, output_file):
    cmd = "animaIsoSurface -i {} -o {}".format(input_file, output_file)
    popen(cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--in_path", help="Path to input label files", required=True)
    parser.add_argument("-o", "--out_path", help="Path to dir where to store .vtk files", required=True)
    parser.add_argument("-m", "--min", help="Lower bound to select labels", type=float, required=True)
    parser.add_argument("-M", "--Max", help="Upper bound to select labels", type=float, required=True)
    
    args = parser.parse_args()
    m, M = args.min, args.max
    in_dir = args.in_path
    out_dir = join(args.out_path, "min_{}_max_{}".format(m, M))
    mkdir(out_dir)
    for file in listdir(in_dir):
        out = join(out_dir, "tmp.nii.gz")
        create_binary_file(join(in_dir, file), out, args.max, args.min)
        name = file.split(".")[0]
        create_vtk(out, join(out_dir, name+".vtk"))

    remove(join(out_dir, "tmp.nii.gz"))