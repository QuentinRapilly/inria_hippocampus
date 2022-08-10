from matplotlib.cbook import ls_mapper
from deformetrica import Deformetrica
import numpy as np
import argparse
from os.path import join, isdir
from os import mkdir, listdir
import json

from kpca_tools import manage_momenta, manage_control_points, compute_eigen_vec

class Shooter:

    def __init__(self, output_path, config_file=None) -> None:

        self.shooting_dir = join(output_path, "shooting")
        if not isdir(self.shooting_dir):
            mkdir(self.shooting_dir)

        self.shooter = Deformetrica(output_dir=self.shooting_dir, verbosity='ERROR')

        self.config_file = config_file

    def reload_config(self):
        """
            The config dict is reloaded after every internal modification to avoid any mistake
            caused by a saved modification that shoudn't be.
        """
        with open(self.config_file,"r") as f:
            self.config = json.load(f)

    def shooting(self, tmin, tmax, start, momenta, control_points):
        # Loads the config dict refering to "shooting"
        self.reload_config()
        cfg = self.config["shooting"].copy()

        # Adds some specific parameters depending to the current call of the method (such as 
        # the name of the files to use for the)

        # template_specification dic modifications
        template_spec = cfg["template_specification"]

        template_spec["start"]["filename"] = start
        # model_options dic modifications
        model_spec = cfg["model_options"]
        model_spec["tmin"] = tmin
        model_spec["tmax"] = tmax
        model_spec["initial_control_points"] = control_points
        model_spec["initial_momenta"] = momenta

        
        # Shooting step 
        self.shooter.compute_shooting(template_spec, model_spec)



def create_and_save_momenta(momenta, kpca_v, keep_dim, coef, output):       
    v = compute_eigen_vec(kpca_vec=kpca_v, momenta=momenta, keep_dim=keep_dim)
    p, q = v.shape

    momenta_dir = join(output, "vp_momenta")
    if not isdir(momenta_dir):
        mkdir(momenta_dir)
    
    momenta_file = join(momenta_dir, "eigen_vec_dim{}_momenta.txt".format(keep_dim))

    with open(momenta_file, "w") as f :
        f.write("1 {} {}\n".format(p,q))
        
        for m in v :
            f.write("\n{} {} {}".format(m[0]*coef, m[1]*coef, m[2]*coef))

    return momenta_file

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-o", "--output")
    parser.add_argument("-C", "--config")
    parser.add_argument("-c", "--control_points")
    parser.add_argument("-m", "--momenta")
    parser.add_argument("-v", "--vtk", help="Mean shape stored as .vtk")
    parser.add_argument("-k", "--kpca", help="K-PCA eigen values and vectors .npz file.")
    parser.add_argument("-d", "--dimension")
    parser.add_argument("-g", "--gamma", help="Mult factor for the shooting momenta")

    args = parser.parse_args()

    kpca_v = np.load(args.kpca)["eigen_vectors"]
    
    momenta_dir = args.momenta
    momenta_files = [join(momenta_dir, filename) for filename in listdir(momenta_dir)]
    momenta, dims = manage_momenta(momenta_files)

    d = int(args.dimension)
    coef = float(args.gamma)
    momenta_file = create_and_save_momenta(momenta=momenta, kpca_v=kpca_v, keep_dim=d, coef=coef, output=args.output)

    shooter = Shooter(args.output, config_file=args.config)
    shooter.shooting(tmin=0, tmax=1, start=args.vtk, momenta=momenta_file, control_points=args.control_points)



