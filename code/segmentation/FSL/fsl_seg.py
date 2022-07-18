from os import popen, listdir, mkdir
from os.path import join, isdir
from shutil import copy2
import argparse

from pkg_resources import require


def fsl_seg(input_file, output_dir, label="L_Hipp,R_Hipp"):
    """
        Launches the segmentation process of FSL on the input_file.
        One can select the labels one want to extract with the argument "label" (ex : L_Hipp,R_Hipp 
        for left and right hippocampus parts)
    """
    if label == None :
        label_cmd = ""
    else :
        label_cmd = " -s "+label

    output = join(output_dir, "seg")
    cmd = "run_first_all{} -d -i {} -o {}".format(label_cmd, input_file, output)

    infos = popen(cmd)
    infos = infos.read()
    
    return infos

def all_fsl_seg(input_dir, output_dir):
    """
        Computes the FSL segmentation of every file in the given input directory.
    """

    print("## Starting segmentation process")

    # Iterates on every file in the input directory
    for filename in listdir(input_dir):
        if True : # filename.find("sub")==0: # the second option is for ASHS bc there are files in imgs dir that arn't imgs
            name = filename.split(".")[0]
            tmp_dir = join(output_dir, name)

            # Creates the dir where the result will be stored
            if not isdir(tmp_dir):
                mkdir(tmp_dir)
            
            print("Processing file : {}".format(filename))
            # Launches the segmentation
            fsl_seg(join(input_dir,filename), tmp_dir)
    
    # Two files will be created (one for the left hippocampus, one for the right), we will store them in
    # appropriate dir
    seg_only_left = join(output_dir,"seg_only_left")
    mkdir(seg_only_left)

    seg_only_right = join(output_dir,"seg_only_right")
    mkdir(seg_only_right)

    print("## Copying the segmentation in a dedicated dir")
    for dirname in listdir(output_dir):
        if dirname.find("seg_only") == -1 :
            current_dir = join(output_dir, dirname)

            for filename in listdir(current_dir):
                # Moves the files in the corresponding dir.
                if filename.find("L_Hipp_first.nii.gz") > -1:
                    to_copy = join(current_dir, filename)
                    destination = join(seg_only_left, dirname+".nii.gz")
                    copy2(to_copy, destination)

                if filename.find("R_Hipp_first.nii.gz") > -1:
                    to_copy = join(current_dir, filename)
                    destination = join(seg_only_right, dirname+".nii.gz")
                    copy2(to_copy, destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="", required=True)
    parser.add_argument("-o", "--output", help="", required=True)

    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output

    all_fsl_seg(input_dir, output_dir)