from os import listdir
from os.path import join
import sys
from nibabel import load

def compare_shapes(imgs_path, labels_path):
    
    for file in sorted(listdir(imgs_path)):
        name = file.split("_")[0]
        img = load(join(imgs_path, file)).dataobj.shape
        label = load(join(labels_path, name+"_label_final.nii.gz")).dataobj.shape

        print("Image {}, shape : {}, label_shape {} (same shape ? : {})".format(name, img, label, img==label))


if __name__ == "__main__":
    imgs_path = sys.argv[1]
    labels_path = sys.argv[2]

    compare_shapes(imgs_path, labels_path)
        
