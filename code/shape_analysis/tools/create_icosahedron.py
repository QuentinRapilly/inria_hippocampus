from meshzoo import icosa_sphere
import vtk
import argparse


if __name__ == "__main__" : 
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--nb_div")

    args = parser.parse_args()
    n = args.nb_div
    points, vertices = icosa_sphere(n)

    v_points = vtk.vtkPoints()
    v_vertices = vtk.vtkCellArray()
    v_pd = vtk.vtkPolyData()
    
    n = points.shape[0]

    v_points.SetNumberOfPoints(n)
    for i in range(n):
        v_points.SetPoint(i, points[i])
        v_vertices.Set
        v_vertices.InsertNextCell(1)
        v_vertices.InsertCellPoint(i)