from random import random
import torch
from torch.utils.data import random_split, DataLoader
from torch.optim import Adam
from torch.optim.lr_scheduler import ExponentialLR
from DeepHippo import DeepHippo
from HippoDataset import HippoDataset 
from Config import Config

def train(model, dataloader, loss_fn, optimizer):
    tot_loss = 0
    for batch in dataloader:
        input, label = batch
        pred = model(input)

        loss = loss_fn(pred,label)
        
        tot_loss += loss.item()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    return tot_loss/len(dataloader)


def test(model, dataloader, loss_fn):
    tot_loss = 0 
    with torch.no_grad():
        for batch in dataloader :
            input, label = batch
            pred = model(input)

            loss = loss_fn(pred,label)
            
            tot_loss += loss.item() 

    return tot_loss/len(dataloader)


def GJL(target, pred):
    #TODO : definir la loss
    return 


def experiment(config):

    device = "cpu"
    if torch.cuda.is_available():
        device = "gpu:0"

    model = DeepHippo(in_channel=config["model"]["in_channel"], n0_channel=config["model"]["n0_channel"],
    mult_channels=config["model"]["mult_channel"], nb_layers=config["model"]["nb_layers"], kernel_size=config["model"]["kernel_size"],
    pool_size=config["model"]["pool_size"], nb_conv_by_layer=config["model"]["nb_conv_layer"], dropout=config["model"]["dropout"],
    nb_labels=config["model"]["nb_labels"])

    model = model.to(device)

    nb_epoch = config["training"]["nb_epoch"]

    dataset = HippoDataset(MRI_path=config["dataset"]["inputs_path"], labels_path=config["dataset"]["labels_path"],device=device)
    n = len(dataset)
    n_train, n_test, n_val = int(n*config["dataset"]["len_train"]), int(n*config["dataset"]["len_test"]), int(n*config["dataset"]["len_val"])
    datasets = random_split(dataset=dataset, lengths=[n_train, n_test, n_val])

    optimizer = Adam(params=model.parameters(), lr=config["training"]["lr"], weight_decay=config["training"]["weight_decay"])

    loss_fn = GJL

    train_dataloader = DataLoader(datasets[0], batch_size=config["training"]["train_batch_size"])
    test_dataloader = DataLoader(datasets[1], batch_size=config["training"]["test_batch_size"])
    val_dataloader = DataLoader(datasets[2], batch_size=config["training"]["val_batch_size"])

    train_loss = list()
    test_loss = list()

    for _ in range(nb_epoch):

        loss = train(model=model, dataloader=train_dataloader, loss_fn=loss_fn, optimizer=optimizer)
        train_loss.append(loss)

        loss = test(model=model, dataloader=test_dataloader, loss_fn=loss_fn)
        test_loss.append(loss)

    loss = test(model=model, dataloader=val_dataloader, loss_fn=loss_fn)

    #TODO : stocker les résultats dans un fichier 

    #TODO : sauvegarder le modele a la fin de l'entrainement


if __name__ == "__init__":
    config = Config().config