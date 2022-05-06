from os import system, listdir
from os.path import isdir, join, splitext
import sys
import argparse


USING_ANIMA = 0
USING_NIBABEL = 1

METHOD = USING_ANIMA

def transform_labels(path_in, path_out):
    """
        Convert a label image from .mnc to .nii.gz using anima functions.
        cmd : animaConvertImage -i <input image> -o <output image> 
    """
    cmd = "animaConvertImage -i {} -o {}".format(path_in,path_out)
    return cmd

def transform_labels_with_model_space(path_in, path_out, path_model):
    """
        Convert a label image from .mnc to .nii.gz using anima functions.
        Set a reference space adjust output's orientation according to model's orientation.
        cmd : animaConvertImage -i <input image> -o <output image> -s <model image>
    """
    cmd = transform_labels(path_in, path_out) + " -s {}".format(path_model)
    return cmd

def process_cmd(cmd):
    """
        Process the bash command given as argument.
    """
    system(cmd)

def sort_model_by_name(model_path):
    """
        Create a dictionnary containing for each subject a list of every of its MRIs. 
    """
    model_list = [file for file in listdir(model_path) if file.find("sub")==0]
    model_dic = {}
    for elem in model_list :
        name = elem.split("_")[0]
        if model_dic.get(name) == None :
            model_dic[name] = [elem]
        else :
            model_dic[name].append(elem)

    return model_dic

def find_corresponding_model(model_dic, name):
    """
        Return the last taken MRI stored in model_dic for a given subject. 
    """
    return sorted(model_dic[name])[0]

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--in_path", help="Path to MRIs to segment", required=True)
    parser.add_argument("-o", "--out_path", help="Path to dir where to store segmetations", required=True)
    parser.add_argument("-m", "--model_path", help = "Path to the location of the images corresponding to the labels", required=True)
    
    args = parser.parse_args()

    in_path = args.in_path
    out_path = args.out_path
    model_path = args.model_path

    # to process every file in a directory
    if isdir(in_path):

        # stores MRIs by subjects
        model_dic = sort_model_by_name(model_path)

        # gets every labels files
        files = [file for file in listdir(in_path) if file.find("sub")==0]

        for file in files:
            name = file.split("_")[0]
            
            if METHOD == USING_ANIMA:
                # calls anima function
                cmd = transform_labels_with_model_space(join(in_path,file), join(out_path,name+".nii.gz"),\
                    join(model_path,find_corresponding_model(model_dic,name)))
                process_cmd(cmd)


    # to process a single file
    """
    else :
        transform_labels(in_path, out_path)
        img = nibabel.load(model_path)
        ornt = img.get_sform()[:3,:3]
        label = nibabel.load(out_path)
        label = label.as_reoriented(ornt)
        nibabel.save(label, out_path)
    """
