import argparse
from os import popen, listdir, mkdir, remove 
from os.path import join, isdir

def create_binary_file(input_file, output_file, upper, lower):
    cmd = "animaThrImage -u {} -t {} -i {} -o {}".format(upper, lower, input_file, output_file)
    infos = popen(cmd)
    infos = infos.read()
    return infos

def add_mask(input1, input2, output):
    cmd = "animaImageArithmetic -i {} -a {} -o {}".format(input1, input2, output)
    infos = popen(cmd)
    infos = infos.read()
    return infos

def create_vtk(input_file, output_file, smoothing = 0, it = 5):
    cmd = "animaIsosurface -i {} -o {} -s {} -I {}".format(input_file, output_file, smoothing, it)
    infos = popen(cmd)
    infos = infos.read()
    return infos

def labels_to_vtk(in_path, out_path, labels, smoothing, iterations):
    if not isdir(out_dir):
        mkdir(out_dir)
    
    for file in listdir(in_dir):
        print("Processing file : {}".format(file))
        final_label = join(out_dir, "final_tmp.nii.gz")
        infos = create_binary_file(join(in_dir, file), final_label, labels[0], labels[0])
        step_label = join(out_dir, "step_tmp.nii.gz")
        for label in labels[1:]:
            infos = create_binary_file(join(in_dir, file), step_label, label, label)
            infos = add_mask(final_label, step_label, final_label)

        name = file.split(".")[0]
        infos = create_vtk(final_label, join(out_dir, name+".vtk"), smoothing, iterations)

    remove(final_label)
    remove(step_label)
    return infos


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--in_path", help="Path to input label files", required=True)
    parser.add_argument("-o", "--out_path", help="Path to dir where to store .vtk files", required=True)
    parser.add_argument("-l", "--labels", help="List of the labels you want to keep (ex : 3,5,8,9)", required=True)
    parser.add_argument("-s", "--smoothing", help="Set the value of the smoothing parameter of 'animaIsosurface'", type=float, default=0)
    parser.add_argument("-I", "--iterations", help="Set the value of the iteration parameter of 'animaIsosurface'", type=int, default=5)
    #parser.add_argument("-m", "--min", help="Lower bound to select labels", type=int, required=True)
    #parser.add_argument("-M", "--max", help="Upper bound to select labels", type=int, required=True)
    
    args = parser.parse_args()
    labels = [int(label) for label in args.labels.split(',')]
    smoothing = args.smoothing
    iterations = args.iterations
    
    #m, M = args.min, args.max
    
    in_dir = args.in_path
    out_dir = join(args.out_path, "label_{}_it_{}_smooth_{}".format(args.labels,iterations,smoothing))

    infos = labels_to_vtk(in_dir, out_dir, labels, smoothing, iterations)