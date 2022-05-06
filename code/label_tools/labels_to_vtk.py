import argparse
from os import popen, listdir, mkdir, remove 
from os.path import join, isdir

def create_binary_file(input_file, output_file, upper, lower):
    cmd = "animaThrImage -u {} -t {} -i {} -o {}".format(upper, lower, input_file, output_file)
    infos = popen(cmd)
    infos = infos.read()
    return infos

def create_vtk(input_file, output_file):
    cmd = "animaIsosurface -i {} -o {}".format(input_file, output_file)
    infos = popen(cmd)
    infos = infos.read()
    return infos


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--in_path", help="Path to input label files", required=True)
    parser.add_argument("-o", "--out_path", help="Path to dir where to store .vtk files", required=True)
    parser.add_argument("-m", "--min", help="Lower bound to select labels", type=int, required=True)
    parser.add_argument("-M", "--max", help="Upper bound to select labels", type=int, required=True)
    
    args = parser.parse_args()
    m, M = args.min, args.max
    in_dir = args.in_path
    out_dir = join(args.out_path, "min_{}_max_{}".format(m, M))
    if not isdir(out_dir):
        mkdir(out_dir)
    for file in listdir(in_dir):
        out = join(out_dir, "tmp.nii.gz")
        infos = create_binary_file(join(in_dir, file), out, args.max, args.min)
        #print("Contenu du dossier avant de creer le vtk : {}".format(listdir(out_dir)))
        name = file.split(".")[0]
        infos = create_vtk(out, join(out_dir, name+".vtk"))

    remove(join(out_dir, "tmp.nii.gz"))