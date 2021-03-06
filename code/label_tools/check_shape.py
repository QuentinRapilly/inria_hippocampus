from os import listdir
from os.path import join
import sys
from nibabel import load


def find_corresponding_model(model_dic, name):
    """
        Return the first taken MRI stored in model_dic for a given subject. 
    """
    return sorted(model_dic[name])[0]


def sort_model_by_name(model_path):
    """
        Create a dictionnary containing for each subject a list of every of its MRIs. 
    """

    # finds every file that refers to an MRI
    model_list = [file for file in listdir(model_path) if file.find("sub")==0]
    model_dic = {}
    for elem in model_list :

        # stores the MRI in a list corresponding to this subject id
        name = elem.split("_")[0]
        if model_dic.get(name) == None :
            model_dic[name] = [elem]
        else :
            model_dic[name].append(elem)

    return model_dic


def compare_shapes(imgs_path, labels_path):

    """
        Compare the shape of label files with the shape of the corresponding MRI files
    """

    # sort the MRI by subjects IDs (according to the fact that severall MRI were taken for each subject)
    imgs_dic = sort_model_by_name(imgs_path)
    
    for file in sorted(listdir(labels_path)):
        name = file.split(".")[0]
        # get the first MRI of the current subject
        img_path = join(imgs_path, find_corresponding_model(imgs_dic, name))
        img = load(img_path).dataobj.shape
        label = load(join(labels_path, file)).dataobj.shape

        print("Image {}, shape : {}, label_shape {} (same shape ? : {})".format(name, img, label, img==label))


if __name__ == "__main__":
    imgs_path = sys.argv[1]
    labels_path = sys.argv[2]

    compare_shapes(imgs_path, labels_path)
        
