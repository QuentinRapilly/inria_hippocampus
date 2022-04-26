from os import system, listdir
from os.path import isdir, join, splitext
import sys

def transform_labels(path_in, path_out, orientation):
    """
    Using the cmd animaConvertImage -i <input image> -o <output image> -R <orientation>
    """
    system("animaConvertImage -i {} -o {} -R ".format(path_in,path_out,orientation))

if __name__ == "__main__":
    in_path, out_path, orientation = sys.argv[1], sys.argv[2], sys.argv[3]

    # to process every file in a directory
    if isdir(in_path):
        for file in listdir(in_path):
            name = splitext(file)[0]
            transform_labels(join(in_path,file),join(out_path,name+".nii.gz"), orientation)

    # to process a single file
    else :
        transform_labels(in_path, out_path, orientation)
