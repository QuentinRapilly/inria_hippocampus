from matplotlib import pyplot as plt
import numpy as np
import argparse


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input")
    parser.add_argument("-o", "--output")

    args = parser.parse_args()

    input, output = args.input, args.output

    data = np.load(input)
    eigen_values = data["eigen_values"]
    y = 100*eigen_values/np.sum(eigen_values)
    y = np.cumsum(y)
    
    plt.bar(x=[i for i in range(1, len(y)+1)], height=y)
    plt.title("Cumulative explained variance (%) according to\nthe number of dim taken into account")
    plt.xlabel("Number of dimension")
    plt.ylabel("Cumulative explained variance(%)")
    plt.legend()

    plt.savefig(output)

    
