from os import listdir, mkdir
from os.path import join
from shutil import copy
import argparse




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input")

    args = parser.parse_args()
    input_dir = args.input

    all_files = join(input_dir,"all_files")
    mkdir(all_files)

    for method in listdir(input_dir):
        if method != "all_files":
            for i, dir_name  in enumerate(listdir(join(input_dir,method))):
                dir = join(input_dir, method, dir_name)
                for filename in listdir(dir):
                    copy(join(dir, filename), join(all_files,"{}_{}_{}".format(method, i, filename)))