from turtle import forward
from torch import nn

class HippoConvLayer(nn.Module):
    def __init__(self, in_channels, out_channels, nb_conv = 3, kernel_size = 3) -> None:
        super().__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.nb_conv = nb_conv
        self.kernel_size = kernel_size

        self.channels = [in_channels] + [out_channels for _ in range(nb_conv)]

        self.conv_list = nn.ModuleList([ 
            nn.Sequential(
                nn.BatchNorm3d(self.channels[i]),
                nn.Conv3d(in_channels=self.channels[i],out_channels=[self.channels[i+1]], kernel_size=kernel_size),
                nn.ReLU()
            )
        for i in range(len(self.channels)-1)])

    def forward(self, inputs):
        x = inputs.copy()
        for i in range(len(self.conv_list)):
            x = self.conv_list[i](x)
        
        return x


class DeepHippo(nn.Module):

    def __init__(self, in_channel = 1, n0_channel = 64, mult_channels = 2,
    nb_layers = 4, kernel_size = 3, nb_conv_by_layer = 3, dropout = 0.5):
        super.__init__()

        self.in_channel = in_channel
        self.nb_channels = [in_channel] + [n0_channel*mult_channels**i for i in range(nb_layers)]

        self.conv_encoder = nn.ModuleList([
            HippoConvLayer(self.nb_channels[i], self.nb_channels[i+1], nb_conv=nb_conv_by_layer, kernel_size=kernel_size)
            for i in range(len(self.nb_channels)-1)
            ])

        self.down_sampling = nn.ModuleList([
            nn.Sequential(nn.MaxPool3d(kernel_size=kernel_size),
            nn.BatchNorm3d(self.nb_channels[i+1])) for i in range(len(self.nb_channels)-1)
        ])

        self.decoder = nn.ModuleList([ 
                HippoConvLayer(in_channels=self.nb_channels[i]+self.nb_channels[i-1], nb_conv=nb_conv_by_layer, kernel_size=kernel_size)
                for i in range(len(self.nb_channels),1,-1)
        ])
            
        self.up_sampling = nn.ModuleList(

        )
    

    def forward(self, input):
        # TODO
        pass
