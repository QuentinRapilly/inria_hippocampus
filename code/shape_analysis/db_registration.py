import argparse
from deformetrica import Deformetrica
import json
from os import listdir, mkdir
from os.path import join, isdir, splitext

class MeanSpaceRegister():
    def __init__(self, input_path, output_path, config_file=None, verbose = False,  logdir = './logdir') -> None:
        
        self.registration_dir = join(output_path, "registration")
        if not isdir(self.registration_dir) :
            mkdir(self.registration_dir)
        
        self.register = Deformetrica(output_dir=self.registration_dir, verbosity='ERROR')

        self.input_path = input_path
        self.shapes = [join(self.input_path, filename) for filename in listdir(input_path)]

    def register(self):
        pass
    
    def register_db(self):
        pass


if __name__ == "__main__":
    pass