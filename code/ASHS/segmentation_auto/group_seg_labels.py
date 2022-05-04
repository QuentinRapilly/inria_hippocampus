from os import popen, listdir
from os.path import join, isdir
import sys 

def cp(input_file, output_file):
    cmd = "cp {} {}".format(input_file, output_file)
    popen(cmd)

if __name__ == "__main__":
    assert(len(sys.argv) > 2)
    in_dir, out_dir = sys.argv[1], sys.argv[2]
    for dir in listdir(in_dir):
        current_dir = join(in_dir, dir)
        if isdir(current_dir) and dir!="workspace" :
            files = listdir(current_dir)
            i = 0
            while files[i].find("layer_002_") != 0 :
                i += 1
            good_file = join(current_dir, files[i])
            print(good_file)
            cp(good_file, join(out_dir,dir+".nii.gz"))

