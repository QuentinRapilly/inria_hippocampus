from os import system, listdir
from os.path import isdir, join, splitext
import sys
import nibabel

def transform_labels(path_in, path_out):
    """
    Using the cmd animaConvertImage -i <input image> -o <output image> 
    """
    system("animaConvertImage -i {} -o {}".format(path_in,path_out))

def sort_model_by_name(model_path):
    model_list = listdir(model_path)
    model_dic = {}
    for elem in model_list :
        name = elem.split("_")[0]
        if model_dic.get(name) == None :
            model_dic[name] = [elem]
        else :
            model_dic[name].append(elem)

    return model_dic

def find_corresponding_model(model_dic, name):
    return sorted(model_dic[name])[-1]

if __name__ == "__main__":
    in_path, out_path, model_path = sys.argv[1], sys.argv[2], sys.argv[3]

    # to process every file in a directory
    if isdir(in_path):
        model_dic = sort_model_by_name(model_path)
        for file in listdir(in_path):
            name = file.split("_")[0]
            transform_labels(join(in_path,file),join(out_path,name+".nii.gz"))

            img = nibabel.load(join(model_path,find_corresponding_model(model_dic,name)))
            ornt = img.get_sform()[:3,:3]
            label = nibabel.load(join(out_path,name+".nii.gz"))
            label = label.as_reoriented(ornt)
            nibabel.save(label,join(out_path,name+".nii.gz"))

    # to process a single file
    else :
        transform_labels(in_path, out_path)
        img = nibabel.load(model_path)
        ornt = img.get_sform()[:3,:3]
        label = nibabel.load(out_path)
        label = label.as_reoriented(ornt)
        nibabel.save(label, out_path)