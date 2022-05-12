from torch import nn, vstack

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
    nb_layers = 4, kernel_size = 3, pool_size = 2,  nb_conv_by_layer = 3, dropout = 0., nb_labels = 1):
        super.__init__()

        self.in_channel = in_channel
        self.nb_channels = [in_channel] + [n0_channel*mult_channels**i for i in range(nb_layers)]

        self.nb_labels = nb_labels
        self.nb_layers = nb_layers

        self.conv_encoder = nn.ModuleList([
            HippoConvLayer(self.nb_channels[i], self.nb_channels[i+1], nb_conv=nb_conv_by_layer, kernel_size=kernel_size)
            for i in range(len(self.nb_channels)-1)
            ])

        self.down_sampling = nn.MaxPool3d(kernel_size=pool_size, return_indices=True)
        self.dropout = nn.Dropout3d(p=dropout) 

        self.conv_decoder = nn.ModuleList([ 
            HippoConvLayer(in_channels=self.nb_channels[i]+self.nb_channels[i-1], out_channels=self.nb_channels[i-1],
            nb_conv=nb_conv_by_layer, kernel_size=kernel_size)
            for i in range(len(self.nb_channels),1,-1)
        ])
            
        self.up_sampling = nn.MaxUnpool3d(stride=pool_size)

        self.heads = nn.ModuleList([ #TODO : renvoyer la sortie de la tete du reseau aux couches de convolution du decoder
            nn.Sequential(nn.Conv3d(in_channels=self.nb_channels[i-1], out_channels=self.nb_labels, kernel_size=kernel_size),
            nn.Softmax(dim=1)) for i in range(len(self.nb_channels),1,-1)
        ])
    

    def forward(self, input):
        
        x = input.copy()
        n = self.nb_layers

        # ENCODER PART  
        x_list = list()
        indexes_list = list()

        for i in range(n):
            # Convolution
            x = self.conv_encoder[i](x)
            
            if i != (n-1):
                x_list.append(x)
                # Pooling/DownSampling
                x, ind = self.down_sampling(x)
                indexes_list.append(ind)
                # DropOut
                x = self.dropout(x)


        out_list = list()
        # DECODER PART 
        for i in range(self.nb_layers-1):
            # Unpooling/UpSampling
            x = self.up_sampling(x, indexes_list[n-2-i]) 
            # -2 because :
            # 1) n is the number of conv layer but they are n-1 pooling operations
            # 2) indexes_list is size n-1 so existing indexes are [0:n-2]

            # Stacking tensors from 
            x = vstack((x_list[n-2-i],x))

            # Convolution
            x = self.conv_decoder[i](x)
            
            # Head of the network
            out = self.heads[i](x)

            out_list.append(out)

        return out_list



        
