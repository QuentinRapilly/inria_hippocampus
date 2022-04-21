from torch.utils.data import Dataset
from torch import tensor
import nibabel
from os import listdir

class HippoDataset(Dataset):

    def __init__(self, MRI_path, labels_path, device = 'cpu') -> None:
        super().__init__()

        self.MRI_list = listdir(MRI_path)
        self.label_list = listdir(labels_path) # TODO : modifier pour que la liste soit dans le même ordre que celle des IRM
        self.device = device
    
    def __getitem__(self, index):
        data = tensor(nibabel.load(self.MRI_list[index]).get_fdata())
        data = data.float().to(self.device)
        label = tensor(nibabel.load(self.MRI_list[index]).get_fdata())
        label = label.float().to(self.device)
        return data, label

    def __len__(self):
        return len(self.MRI_list)