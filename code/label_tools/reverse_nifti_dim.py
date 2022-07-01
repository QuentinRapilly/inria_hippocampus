import nibabel
import numpy as np
from os import listdir
from os.path import join

import argparse


"""
This file isn't used anymore, it was an attempt to correct the shift after the conversion from mnc to nifti.
This isn't an issue anymore with minctoolkit.
"""

def reverse_file(input_file, output_file, dims = (0,1), using_header = False, verbose = False):

    if verbose :
        print("Processing file : {}".format(input_file))
    nii = nibabel.load(input_file)
    data = nii.get_fdata()
    new_data = np.flip(data, dims)
    if verbose : 
        print("Values in data : {}".format(np.unique(data)))
    #TODO modifier le header pour changer l'orientation
    sform = nii.get_sform()
    if verbose : 
        print("sform before : {}".format(sform)) 
    mat = np.eye(4)
    for d in dims:
        mat[d,d] = -mat[d,d]
    sform = mat @ sform 

    if verbose : 
        print("sform after : {}".format(sform))
    
    if using_header:
        nii.set_sform(sform)
        new_img = nibabel.nifti1.Nifti1Image(new_data, sform, nii.header)
    else :
        new_img = nibabel.nifti1.Nifti1Image(new_data, sform)

    if verbose : 
        print("Values after creating new image : {}".format(np.unique(new_img.get_fdata())))

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