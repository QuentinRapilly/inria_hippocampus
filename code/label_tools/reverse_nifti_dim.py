import nibabel
import numpy as np
from os import listdir
from os.path import join

import argparse

def reverse_file(input_file, output_file, dims = (0,1), using_header = False):

    nii = nibabel.load(input_file)
    data = nii.get_fdata()
    new_data = np.flip(data, dims)
    #TODO modifier le header pour changer l'orientation
    sform = nii.get_sform()
    mat = np.eye(4)
    for d in dims:
        mat[d,d] = -mat[d,d]
    sform = sform @ mat
    
    if using_header:
        nii.set_sform(sform)
        new_img = nibabel.nifti1.Nifti1Image(new_data, sform, nii.header)
    else :
        new_img = nibabel.nifti1.Nifti1Image(new_data, sform)

    new_img.to_filename(output_file)


def reverse_dir(input_dir, output_dir, dims = (0, 1)):

    for filename in listdir(input_dir):
        input_file = join(input_dir, filename)
        output_file = join(output_dir, filename)

        reverse_file(input_file, output_file, dims)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-i", "--input", help="Input dir", required=True)
    parser.add_argument("-o", "--output", help="Output dir", required=True)
    parser.add_argument("-d", "--dimensions", help="Dimensions to flip (ex : '0,1')", default="0,1")

    args = parser.parse_args()

    dims = [int(d) for d in args.dimensions.split(',')]

    reverse_dir(args.input, args.output, dims)