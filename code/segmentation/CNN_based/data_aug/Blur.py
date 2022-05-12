from turtle import forward
from typing import List
from torch import nn, rand, tensor, exp, sqrt
from torch.nn.functional import conv1d, conv2d, conv3d
import math

class BlurFilter(nn.Module):

    def __init__(self, size : int = 10, dim : int = 2, sigma_min : float = 0.1, sigma_max : float = 5) -> None:
        super().__init__()

        self.size = size
        self.k = (size + 1)/2
        self.dim = dim
        self.sigma_min = sigma_min
        self.sigma_max = sigma_max

        if dim == 1:
            self.f = conv1d
        elif dim == 2:
            self.f = conv2d
        elif dim == 3:
            self.f = conv3d
        else : 
            raise Exception("Too high dimension to manage it this way")

    def forward(self, x):
        print(x.shape)
        sigma = (self.sigma_max - self.sigma_min)*rand((1)) + self.sigma_min
        if self.dim == 1:
            filter =[(k-self.k)**2 for k in range(self.size)]
        elif self.dim == 2:
            filter = [[(j-self.k)**2 + (k-self.k)**2 for k in range(self.size)] for j in range(self.size)]
        elif self.dim == 3:
            filter = [[[(i-self.k)**2 + (j-self.k)**2 + (k-self.k)**2 for k in range(self.size)] for j in range(self.size)] for i in range(self.size)]
        filter = tensor(filter)
        filter = (1/(sqrt(tensor(2*math.pi))*sigma)**self.dim)*exp(-filter/(2*sigma**2))
        filter = filter/sum(filter)
        filter = filter.unsqueeze(0)
        filter = filter.expand(x.shape[0], -1, -1)
        print(filter.shape)
        res = self.f(x, filter, padding="same")
        return res



if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt
    blur = BlurFilter()
    img_path = sys.argv[1]
    
    img = tensor(plt.imread(img_path))
    img = img.permute((2,0,1))
    res = blur(img)
    plt.imshow(res)
    plt.show()

