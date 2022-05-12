import argparse
from deformetrica import Deformetrica
import json
from os import listdir
from os.path import join

class IterativBarycentre():
    def __init__(self, input_path, output_path, config=None) -> None:
        self.dfca = Deformetrica(output_dir='output', verbosity='INFO')
        self.input_path = input_path
        self.shapes = listdir(input_path)
        assert len(self.shapes) > 1
        self.output_path = output_path
        self.config = config



    def registration(self):
        #TODO
        pass

    def shooting(self):
        #TODO
        pass

    def iterativ_barycentre(self):
        shape1 = self.shapes.pop()
        shape2 = self.shape.pop()
        traj = self.registration(shape1, shape2)
        mean = self.shooting(traj, 0.5)
        i = 2

        while len(self.shape) > 0:
            shape = self.shape.pop
            traj = self.registration(mean, shape)
            i += 1
            mean = self.shooting(traj, 1/i)

        pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--in_path", help="Dir where the shapes are stored", required=True)
    parser.add_argument("-o", "--out_path", help="Dir where to store the log relative to the algorithm and the result",\
        required=True)
    parser.add_argument("-c", "--config", help="Path to the config file", default=None)
    
    args = parser.parse_args()

    if args.config != None:
        config = json.load(args.config)
    else :
        config = None

    algo = IterativBarycentre(args.in_path, args.out_path, config)

    algo.iterativ_barycentre()

    