from os import popen, listdir
from os.path import join
from stat import filemode
import argparse

def change_resolution(input, output, res = [1,1,1]):
    cmd = "animaImageResolutionChanger -n nearest -z {} -y {} -x {} -o {} -i {}".format(res[0],\
        res[1], res[2], input, output)
    infos = popen(cmd)
    infos = infos.read()
    return infos 

def change_dir_res(input_dir, output_dir, res):

    for filename in listdir(input_dir):
        
        input = join(input_dir, filename)
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