import argparse
from fileinput import filename
from shutil import copy2
from os import listdir
from os.path import join, splitext
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input")
    parser.add_argument("-o", "--output")
    
    args = parser.parse_args()
    input = args.input
    output = args.output

    for dirname in listdir(input):
        current_dir = join(input, dirname)
        i = 0
        all_files = listdir(current_dir)
        while all_files[i].find("Momenta")<0:
            i += 1
            
        to_move = join(current_dir, all_files[i])
        loc = join(output, dirname+"_momenta.txt")
        copy2(to_move, loc)
    