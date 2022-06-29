import argparse
from atexit import register
from deformetrica import Deformetrica
import json
from os import listdir, mkdir
from os.path import join, isdir, splitext, basename

class MeanSpaceRegister():

    """
        This class is inspired by the one defined in the iterativ_barycentre.py file.
        Here are defined every functions necessary to register the shapes in our database
        to the mean shape space (computed by the iterative barycentre algorithm).
    """

    def __init__(self, input_path, output_path, mean_shape, config_file=None, verbose = False,  logdir = './logdir') -> None:
        
        self.registration_dir = join(output_path, "registration")
        if not isdir(self.registration_dir) :
            mkdir(self.registration_dir)
        

        self.input_path = input_path
        self.shapes = [join(self.input_path, filename) for filename in listdir(input_path)]

        self.output_path = output_path
        self.config_file = config_file

        self.mean_shape = mean_shape

    
    def reload_config(self):
        """
            The config dict is reloaded after every internal modification to avoid any mistake
            caused by a saved modification that shoudn't be.
        """
        with open(self.config_file,"r") as f:
            self.config = json.load(f)

    def init_register(self, dir):
        """
            Creates a Deformetrica object (that can call the API) with the good result storing
            directory after each step. 
        """
        self.dfca = Deformetrica(output_dir=dir, verbosity='ERROR')

    def register(self, mean_shape, shape, dir):
        """
            Applies the registration operation from the mean shape to the choosen shape.
        """
        self.reload_config()
        cfg = self.config["registration"].copy()

        # template_specification dic modifications
        template_spec = cfg["template_specification"]
        template_spec["shape"]["filename"] = mean_shape

        # dataset_options dic modifications
        dataset_spec = cfg["dataset_specification"]
        dataset_spec["dataset_filenames"].append([{"shape" : shape}])
        dataset_spec["subject_ids"].append("target")

        model_spec = cfg["model_options"]

        estimator_spec = cfg["estimator_options"]

        self.init_register(dir)

        self.dfca.estimate_registration(template_spec, dataset_spec, model_spec, estimator_spec)
        
    
    def register_db(self):

        """
            Applies the registration process for every file in the input directory.
        """
        
        for filename in self.shapes:

            short_name = basename(filename)
            print("Processing file : {}".format(filename))
            tmp_dir_name = splitext(short_name)[0]
            dir_name = join(self.output_path, tmp_dir_name)

            if not isdir(dir_name) :
                mkdir(dir_name)
            
            self.register(self.mean_shape, filename, dir_name)
            


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="Input dir containing the files to register")
    parser.add_argument("-o", "--output", help="Output file where to store the results")
    parser.add_argument("-m", "--mean_shape", help="Path to the mean shape")
    parser.add_argument("-c", "--config", help="Config file")

    args = parser.parse_args()

    algo = MeanSpaceRegister(args.input, args.output, args.mean_shape, args.config)

    algo.register_db()