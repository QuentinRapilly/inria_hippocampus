from os import popen, listdir, mkdir
from os.path import join, isdir
import argparse
from ntpath import basename

def registration(mni, input, output, transform):
    """
        This function is used to find the transformation one need to apply to convert the input image in the 
        MNI space given as argument.
            - output : is where the input is stored once the transformation is applied.
            - transform : is where the corresponding transformation is stored
    """
    cmd = "animaPyramidalBMRegistration -r {} -m {} -o {} -O {} --ot 2".format(mni, input, output, transform)
    infos = popen(cmd)
    infos = infos.read()
    return infos

def transformation(input, mni, transform, output):
    """
        This functions applies the transformation given as argument to the input image.
        It is usefull to move some label files in the MNI space once the transformation has already been computed
        for the corresponding MRI.
    """
    cmd = "animaApplyTransformSerie -i {} -g {} -t {} -o {} -n nearest".format(input, mni, transform, output)
    infos = popen(cmd)
    infos = infos.read()
    return infos

def create_xml_transformation(input, output):
    """
        Modifies the way the input transformation is stored to match the "transformation" method
        requirements (txt=>xml)
    """
    cmd = "animaTransformSerieXmlGenerator -i {} -o {}".format(input, output)
    infos = popen(cmd)
    infos = infos.read()
    return infos

def to_mni(images_path, labels_path, mni_path, output_path, split_label_at = "."):
    """
    For every image in the given directory, computes the transformation necessary to register it into the
    MNI space. Then apply this transformation to the corresponding label file.
    """

    # We check if there is not already a dir containing relocated images and then create it
    images_out = join(output_path, "images")
    assert not isdir(images_out)
    mkdir(images_out)

    # Same for transformations
    transform_out = join(output_path, "transform")
    assert not isdir(transform_out)
    mkdir(transform_out)

    # Same for labels 
    labels_out = join(output_path, "labels")
    assert not isdir(labels_out)
    mkdir(labels_out)

    transform_txt = join(transform_out, "txt_files")
    mkdir(transform_txt)
    transform_xml = join(transform_out, "xml_files")
    mkdir(transform_xml)
    
    sub_dic = {}

    print("Step 0 : Sorting files")

    # as we have severall runs for each subject, we sort them by subject and keep only one
    for filename in listdir(images_path):
        if True : # filename.find("sub")==0: # Modifs pour ADNI (et plus Rajah)
            sub = filename.split(".")[0] # filename.split("_")[0] # Modifs pour ADNI (et plus Rajah)
            if sub_dic.get(sub) == None:
                sub_dic[sub] = [filename]
            else :
                sub_dic[sub].append(filename)

    images = [join(images_path, sorted(sub_dic[sub])[0]) for sub in sub_dic]

    transform_dic = {}

    print("Step 1 : Creating transformation for images")
    for image in images :
        # For each image, find the transformation and apply it to the image
        sub = basename(image).split(".")[0] # basename(image).split("_")[0]  # Modifs pour ADNI (et plus Rajah)
        img_out = join(images_out, sub+".nii.gz")
        tsf_out = join(transform_txt, sub+".txt")

        registration(mni_path, image, img_out, tsf_out)

        tsf_xml = join(transform_xml, sub+".xml")
        create_xml_transformation(tsf_out, tsf_xml)

        transform_dic[sub] = tsf_xml

    labels = [join(labels_path, filename) for filename in listdir(labels_path)]

    print("Step 2 : Applying obtained transfomration on labels")

    for label in labels:
        # For each label file, finds the corresponding transformation and applies it
        sub = basename(label).split(split_label_at)[0] 
        lab_out = join(labels_out, sub+".nii.gz")
        tsf = transform_dic[sub]

        transformation(label, mni_path, tsf, lab_out)


def to_mni_with_transformation(transformation_path, labels_path, mni_path, output_path, split_label_at = "."):
    """
        Apply the transformation to the label files if the have all already been computed.
    """
    
    assert isdir(output_path)
    transform_dic = {}

    for tsf in listdir(transformation_path):
        sub = tsf.split(".")[0]
        transform_dic[sub] = join(transformation_path, tsf)
    
    for label in listdir(labels_path):
        sub = label.split(split_label_at)[0]

        tsf = transform_dic[sub]
        #print("transformation path : {}".format(tsf))
        lab_out = join(output_path, sub+".nii.gz")
        lab_in = join(labels_path, label)
        #print("lab_in path : {}".format(lab_in))
        transformation(lab_in, mni_path, tsf, lab_out)


if __name__ == "__main__" :
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--images", default=None, help="Dir where the images are stored")
    parser.add_argument("-l", "--labels", help="Dir where the labels are stored", required=True)
    parser.add_argument("-o", "--output", help="Dir where to store the result",\
        required=True)
    parser.add_argument("-t", "--transform", default=None, help="Dir where to find the transformation\
        if they have already been computed before")
    parser.add_argument("-m", "--mni", help="Path to the MNI model file", required=True)

    parser.add_argument("-M", "--method", default="random", choices=["compute", "use"], help="Choosing the method :\
        'compute' - computing transform from images, 'use' - using existing ")
    
    args = parser.parse_args()

    method = args.method
    assert ((args.images != None and method == "compute") or (args.transform != None and method == "use"))

    if method == "compute":
        to_mni(args.images, args.labels, args.mni, args.output)
    if method == "use":
        to_mni_with_transformation(args.transform, args.labels, args.mni, args.output)
