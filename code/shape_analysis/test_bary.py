import argparse
from os.path import join

from iterativ_barycentre import IterativBarycentre


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--in_path", help="Dir where the shapes are stored", required=True)
    parser.add_argument("-o", "--out_path", help="Dir where to store the log relative to the algorithm and the result",\
        required=True)
    parser.add_argument("-c", "--config", help="Path to the config file", default=None)

    parser.add_argument("-v", "--verbose", choices=["yes", "no"], default="no")
    parser.add_argument("-w", "--weight", type=float, help="Weight for the shooting", default=1.0)
    
    args = parser.parse_args()

    verbose = (args.verbose == "yes")

    algo = IterativBarycentre(args.in_path, args.out_path, args.config, verbose=verbose, rm_at_each_step=False)

    shape0 = algo.shapes[0]
    shape1 = algo.shapes[1]

    algo.registration(shape0, shape1)

    momenta = join(algo.registration_dir, "DeterministicAtlas__EstimatedParameters__Momenta.txt")
    control_points = join(algo.registration_dir, "DeterministicAtlas__EstimatedParameters__ControlPoints.txt")

    algo.shooting(args.weight, shape0, momenta, control_points)