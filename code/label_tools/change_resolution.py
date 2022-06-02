from os import popen, listdir
from os.path import join
from stat import filemode
import argparse

def change_resolution(input, output, res = [1,1,1]):

    """
        Change the resolution of a given input MRI to match the resolution given as input.
        inputs :
          - input : the input MRI
          - output : where to store the result
          - res List[float] : list containing in this order, the new resolution on axis z, y then x
    """

    cmd = "animaImageResolutionChanger -n nearest -z {} -y {} -x {} -i {} -o {}".format(res[0],\
        res[1], res[2], input, output)
    infos = popen(cmd)
    infos = infos.read()
    return infos 

def change_dir_res(input_dir, output_dir, res):

    """
        Change the resolution of every images in a given directory and store them in the choosen output_dir.
        inputs :
          - input_dir : dir where the images are stored
          - output_dir : dir where the post processed images will be stored
          - res List[float] : list containing in this order, the new resolution on axis z, y then x
    """

    for filename in listdir(input_dir):
        
        input = join(input_dir, filename)

        print("En train de traiter : {}".format(input))

        output = join(output_dir, filename)

        infos = change_resolution(input=input, output=output, res=res)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Path to input images dir")
    parser.add_argument("-o", "--output", help="Path to output dir")
    parser.add_argument("-r", "--resolution", default="1,1,1", help="z,y,x axes resolution")

    args = parser.parse_args()

    resolution = [float(elem) for elem in args.resolution.split(',')]

    succes = change_dir_res(args.input, args.output, resolution)