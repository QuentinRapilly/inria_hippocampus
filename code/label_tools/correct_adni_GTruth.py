import nibabel as nb
import numpy as np
from os import listdir
from os.path import join
import argparse 


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--input", help = "")
  parser.add_argument("-o", "--output", help = "")

  args = parser.parse_args()
  input, output = args.input, args.output
  for crt_file in listdir(input):
    img = nb.load(join(input, crt_file))
    data = img.get_fdata()
    new_data = (data == np.max(data))*1.
    new_img = nb.nifti1.Nifti1Image(new_data, img.get_affine(), header = img.get_header())
    nb.save(new_img,join(output, crt_file))
