import argparse
from deformetrica import Deformetrica
import json
from os import listdir, mkdir, unlink
from os.path import join, isdir, splitext, isfile, islink
from shutil import rmtree
import numpy as np
from datetime import datetime
from time import time

class IterativBarycentre():

    def __init__(self, input_path, output_path, config_file=None, verbose = False,  logdir = './logdir', rm_at_each_step = True, starting_point = None) -> None:
        self.registration_dir = join(output_path, "registration")
        if not isdir(self.registration_dir) :
            mkdir(self.registration_dir)
        self.shooting_dir = join(output_path, "shooting")
        if not isdir(self.shooting_dir):
            mkdir(self.shooting_dir)
        self.register = Deformetrica(output_dir=self.registration_dir, verbosity='ERROR')
        self.shooter = Deformetrica(output_dir=self.shooting_dir, verbosity='ERROR')

        self.input_path = input_path
        self.shapes = [join(self.input_path, filename) for filename in listdir(input_path)]
        assert len(self.shapes) > 1
        self.output_path = output_path
        self.config_file = config_file
        self.logdir = logdir
        self.verbose = verbose
        if self.verbose :
            if not isdir(self.logdir) : mkdir(self.logdir)

        self.rm_at_each_step = rm_at_each_step
        self.starting_point = starting_point
        if starting_point != None :
            self.shapes.remove(starting_point)

    def reload_config(self):
        """
            The config dict is reloaded after every internal modification to avoid any mistake
            caused by a saved modification that shoudn't be.
        """
        with open(self.config_file,"r") as f:
            self.config = json.load(f)

    def clean_dir(self, path_to_dir):
        """
            Remove everything in a directory. This method is called to clean the registration and shooting
            directories between steps to be sure there are no conflicts between files.
        """
        for filename in listdir(path_to_dir):
            file_path = join(path_to_dir, filename)
            try :
                if isfile(file_path) or islink(file_path):
                    unlink(file_path)
                elif isdir(file_path):
                    rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


    def registration(self, shape1, shape2):

        # Loads the config dict refering to "registration"
        self.reload_config()
        cfg = self.config["registration"].copy()

        # Adds some specific parameters depending to the current call of the method (such as 
        # the name of the files to use for the)

        # template_specification dic modifications
        template_spec = cfg["template_specification"]
        template_spec["shape"]["filename"] = shape1

        # dataset_options dic modifications
        dataset_spec = cfg["dataset_specification"]
        dataset_spec["dataset_filenames"].append([{"shape" : shape2}])
        dataset_spec["subject_ids"].append("target")

        model_spec = cfg["model_options"]

        estimator_spec = cfg["estimator_options"]
        
        # Writes the parameters in logs files 
        if self.verbose :
            with open(join(self.logdir, "registration_{}.txt".format(datetime.fromtimestamp(time()))),"w") as f_out :
                print("## Template spec :\{}".format(json.dumps(template_spec, indent=4)), file=f_out)
                print("## Dataset spec :\{}".format(json.dumps(dataset_spec, indent=4)), file=f_out)
                print("## Model options :\{}".format(json.dumps(model_spec, indent=4)), file=f_out)
                print("## Estimator options :\{}".format(json.dumps(estimator_spec, indent=4)), file=f_out)
        
        # Registration step
        self.register.estimate_registration(template_spec, dataset_spec, model_spec, estimator_spec)

        # Clean the other dir
        if self.rm_at_each_step : self.clean_dir(self.shooting_dir)


    def shooting(self, weight, start, momenta, control_points):
        # Loads the config dict refering to "shooting"
        self.reload_config()
        cfg = self.config["shooting"].copy()

        # Adds some specific parameters depending to the current call of the method (such as 
        # the name of the files to use for the)

        # template_specification dic modifications
        template_spec = cfg["template_specification"]

        template_spec["start"]["filename"] = join(self.registration_dir,\
            start)
        # model_options dic modifications
        model_spec = cfg["model_options"]
        model_spec["tmax"] = weight
        model_spec["initial_control_points"] = join(self.registration_dir,\
            control_points) # "DeterministicAtlas__EstimatedParameters__ControlPoints.txt"
        model_spec["initial_momenta"] = join(self.registration_dir,\
            momenta) # "DeterministicAtlas__EstimatedParameters__Momenta.txt"

        # Writes the parameters in logs files 
        if self.verbose :
            with open(join(self.logdir, "shooting_{}.txt".format(datetime.fromtimestamp(time()))),"w") as f_out :
                print("## Template spec :\{}".format(json.dumps(template_spec, indent=4)), file=f_out)
                print("## Model options :\{}".format(json.dumps(model_spec, indent=4)), file=f_out)
        
        # Shooting step 
        self.shooter.compute_shooting(template_spec, model_spec)

        if self.rm_at_each_step : self.clean_dir(self.registration_dir)


    def iterativ_barycentre(self):
        """
            This methods computes the whole algorithm of iterativ barycentre :
                - iterates on every shape of the dataset
                - compute the trajectory from the mean shape to the new one
                - shoot along the trajectory to the new mean shape
        """

        # Select two initial shapes to compute a first mean between them
        if self.starting_point == None :
            shape1 = self.shapes.pop()
        else :
            shape1 = self.starting_point
        shape2 = self.shapes.pop()
        print("Etape de registration initiale, fichiers utilises :\n{}\n{}".format(shape1,shape2))
        self.registration(shape1, shape2)
        i = 2
        start = join(self.registration_dir, "DeterministicAtlas__flow__shape__subject_target__tp_0.vtk")
        momenta = join(self.registration_dir, "DeterministicAtlas__EstimatedParameters__Momenta.txt")
        control_points = join(self.registration_dir, "DeterministicAtlas__EstimatedParameters__ControlPoints.txt")
        print("Etape de shooting initiale, fichiers utilises :\nStart : {}\nMomenta : {}\nControl Points : {}"\
                .format(start, momenta, control_points))
        self.shooting(1/i, start=start, momenta=momenta, control_points=control_points)

        # Then apply the process for the whole dataset
        cpt = 0
        while len(self.shapes) > 0:
            cpt += 1
            shape = self.shapes.pop()

            # The file to consider is always the one with the highest time in the shooting dir as we
            # precise the max time. 
            mean_tab = [filename for filename in listdir(self.shooting_dir) if filename.find("start")>=0]
            idx = [float(splitext(filename)[0].split("_")[-1]) for filename in mean_tab]
            indexes = np.argmax(idx)
            
            mean = join(self.shooting_dir, mean_tab[indexes])
            print("Etape de registration {}, fichiers utilises :\n{}\n{}".format(cpt,shape,mean))
            self.registration(mean, shape)
            i += 1
            
            print("Etape de shooting {}, fichiers utilises :\nStart : {}\nMomenta : {}\nControl Points : {}"\
                .format(cpt, start, momenta, control_points))
            self.shooting(1/i, start=start, momenta=momenta, control_points=control_points)
            # Same start, momenta and control_points (path are the same but they have been updated)

        mean_tab = [filename for filename in listdir(self.shooting_dir) if filename.find("start")>=0]
        idx = [float(splitext(filename)[0].split("_")[-1]) for filename in mean_tab]
        indexes = np.argmax(idx)
        mean = join(self.shooting_dir, mean_tab[indexes])

        return mean



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--in_path", help="Dir where the shapes are stored", required=True)
    parser.add_argument("-o", "--out_path", help="Dir where to store the log relative to the algorithm and the result",\
        required=True)
    parser.add_argument("-c", "--config", help="Path to the config file", default=None)
    parser.add_argument("-v", "--verbose", choices=["yes", "no"], default="no")
    parser.add_argument("-s", "--start", default = None, help="Use this argument to precise a given file to start the algorithm")
    
    args = parser.parse_args()

    verbose = (args.verbose == "yes")

    start = args.start

    algo = IterativBarycentre(args.in_path, args.out_path, args.config, verbose=verbose, starting_point = start)

    mean = algo.iterativ_barycentre()

    print("Mean shape stored at : {}".format(mean))

    