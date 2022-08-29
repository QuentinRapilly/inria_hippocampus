import pyvista as pv
import numpy as np
import argparse 

def compute_heatmap(mean_mesh, shooted_mesh, output):

    mean_points = mean_mesh.points
    shooted_points = shooted_mesh.points

    diff = shooted_points-mean_points

    field = np.linalg.norm(diff, ord=2, axis=1)

    shooted_mesh.point_data["deformation"] = field

    shooted_mesh.save(output)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-i1", "--input1", help="Mean shape")
    parser.add_argument("-i2", "--input2", help="Shape after shooting")
    parser.add_argument("-o", "--output")

    args = parser.parse_args()


    mean_mesh = pv.read(args.input1)
    shooted_mesh = pv.read(args.input2)

    compute_heatmap(mean_mesh, shooted_mesh, args.output)