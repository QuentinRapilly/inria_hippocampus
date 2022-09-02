import pyvista as pv 
import argparse
from os import listdir
from os.path import join

def compute_volume(input_dir, output_file):
    with open(output_file, "a") as f:
        for filename in listdir(input_dir):
            mesh = pv.read(join(input_dir,filename))
            mesh.compute_cell_sizes()

            f.write("{},{}mm3".format(filename, round(mesh.volume,ndigits=4)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir")
    parser.add_argument("-o", "--output_file")

    args = parser.parse_args()

    compute_volume(args.input_dir, args.output_file)

