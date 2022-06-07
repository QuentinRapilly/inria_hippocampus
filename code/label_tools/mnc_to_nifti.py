from os import system, listdir, popen, mkdir
from os.path import isdir, join, splitext
import argparse


USING_ANIMA = 0
USING_MINC = 1

METHOD = USING_MINC

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

def create_float_file(path_in, path_out):

    cmd = "mincreshape -float {} {}".format(path_in, path_out)
    infos = popen(cmd)
    infos = infos.read()

    return infos

def minc_mnc2nii(path_in, path_out):
    cmd = "mnc2nii -nii {} {}".format(path_in, path_out)
    infos = popen(cmd)
    infos = infos.read()

    return infos

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

def mnc_to_nifti(in_path, out_path, model_path, using_model = True, verbose = True):
    # to process every file in a directory
    if isdir(in_path):

        # stores MRIs by subjects
        model_dic = sort_model_by_name(model_path)

        # gets every labels files
        files = [file for file in listdir(in_path) if file.find("sub")==0]

        for file in files:
            
            if verbose : print("Processing file : {}".format(file))
            
            name = file.split("_")[0]
            
            if METHOD == USING_ANIMA:
                # calls anima function
                if using_model :
                    model_space = find_corresponding_model(model_dic,name)
                    if verbose : print("Using model : {}".format(model_space))
                    cmd = transform_labels_with_model_space(join(in_path,file), join(out_path,name+".nii.gz"),\
                        join(model_path,model_space))
                else :
                    cmd = transform_labels(join(in_path,file), join(out_path,name+".nii.gz"))                
                process_cmd(cmd)


def mnc2nii_dir(path_in, path_out):
    float_dir = join(path_out, "float_files")
    out_dir = join(path_out, "nii_files")
    if not isdir(float_dir) : mkdir(float_dir)
    if not isdir(out_dir) : mkdir(out_dir)

    files = [file for file in listdir(in_path) if file.find("sub")==0]
    for filename in files:
        name = filename.split(".")
        
        float_file = join(float_dir, filename)
        nii_file = join(out_dir, name+".nii")

        create_float_file(join(path_in, filename), float_file)
        minc_mnc2nii(float_file, nii_file)



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--in_path", help="Path to MRIs to segment", required=True)
    parser.add_argument("-o", "--out_path", help="Path to dir where to store segmetations", required=True)
    parser.add_argument("-m", "--model_path", help = "Path to the location of the images corresponding to the labels")
    parser.add_argument("-M", "--using_model", choices=["yes", "no"], default="no", help="Boolean : True = using the corresponding MRI as reference space\
        False = not using it.")

    args = parser.parse_args()

    in_path = args.in_path
    out_path = args.out_path
    model_path = args.model_path
    using_model = (args.using_model == "yes")

    #mnc_to_nifti(in_path, out_path, model_path, using_model)

    mnc2nii_dir(in_path, out_path)


