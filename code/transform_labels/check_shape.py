from os import listdir
from os.path import join
import sys
from nibabel import load
from sklearn import naive_bayes

def compare_shapes(imgs_path, labels_path):
    
    for file in listdir(imgs_path):
        name = file.split("_")[0]
        img = load(join(imgs_path, file)).dataobj
        label = load(join(labels_path, name+"_label_final.nii.gz")).dataobj

        print("Image {}, shape : {}, label_shape {}".format(name, img.shape, label.shape))


if __name__ == "__main__":
    imgs_path = sys.argv[1]
    labels_path = sys.argv[2]

    compare_shapes(imgs_path, labels_path)
        
