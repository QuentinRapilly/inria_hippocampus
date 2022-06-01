import argparse
from re import template
from deformetrica import Deformetrica
import json
from os import listdir, mkdir
from os.path import join, isdir, splitext
import numpy as np

class IterativBarycentre():

    def __init__(self, input_path, output_path, config=None) -> None:
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
        self.config = config


    def registration(self, shape1, shape2):
        cfg = self.config["registration"].copy()

        # template_specification dic modifications
        template_spec = cfg["template_specification"]
        template_spec["shape"]["filename"] = shape1

        # dataset_options dic modifications
        dataset_spec = cfg["dataset_specification"]
        dataset_spec["dataset_filenames"].append([{"shape" : shape2}])
        dataset_spec["subject_ids"].append("target")

        model_options = cfg["model_options"]

        estimator_options = cfg["estimator_options"]
        
        # registration
        self.register.estimate_registration(template_spec, dataset_spec, model_options, estimator_options)


    def shooting(self, weight, start, momenta, control_points):
        cfg = self.config["shooting"].copy()

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

        # shooting 
        self.shooter.compute_shooting(template_spec, model_spec)


    def iterativ_barycentre(self):

        shape1 = self.shapes.pop()
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

        while len(self.shapes) > 0:
            shape = self.shapes.pop()

            mean_tab = [filename for filename in listdir(self.shooting_dir) if filename.find("stop")>=0]
            idx = [float(splitext(filename).split("_")[-1]) for filename in mean_tab]
            indexes = np.argmax(idx)
            mean = join(self.shooting_dir, mean_tab[indexes])
            print("Etape de registration initiale, fichiers utilises :\n{}\n{}".format(shape,mean))
            self.registration(mean, shape)
            i += 1
            
            print("Etape de shooting initiale, fichiers utilises :\nStart : {}\nMomenta : {}\nControl Points : {}"\
                .format(start, momenta, control_points))
            self.shooting(1/i, start=start, momenta=momenta, control_points=control_points)
            # Same start, momenta and control_points (path are the same but they have been updated)

        mean_tab = [filename for filename in listdir(self.shooting_dir) if filename.find("stop")>=0]
        idx = [float(splitext(filename).split("_")[-1]) for filename in mean]
        indexes = np.argmax(idx)
        mean = join(self.shooting_dir, mean_tab[indexes])

        return mean



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--in_path", help="Dir where the shapes are stored", required=True)
    parser.add_argument("-o", "--out_path", help="Dir where to store the log relative to the algorithm and the result",\
        required=True)
    parser.add_argument("-c", "--config", help="Path to the config file", default=None)
    
    args = parser.parse_args()

    if args.config != None:
        with open(args.config,"r") as f:
            config = json.load(f)
    else :
        config = None

    algo = IterativBarycentre(args.in_path, args.out_path, config)

    mean = algo.iterativ_barycentre()

    print("Mean shape stored at : {}".format(mean))

    