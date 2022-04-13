# Tools 

## Segmentation methods 
### How to use ASHS ?

Two methods exists :
* 1) An easy one : using ITK-SNAP and cloud computing.
* 2) A more developped one : downloading ASHS codes and running it on your own device.

#### Easy method : Cloud

1) You should start by downloading ITK-SNAP 3.8 or later (http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.SNAP3)

2) Follow the instructions given on this guide : https://sites.google.com/view/ashs-dox/cloud-ashs/cloud-ashs-for-t1-mri?authuser=0

#### Developped method : on your own device

This method requires a Linux or Mac OS operating system.

>**Advantages :**
This method gives more liberties, especially if we want to process severall segmentations automatically rather than uploading every one of them on the cloud following the first method.
Moreover, it safer not to upload sensitives data on a cloud plateform regarding data sovereignty.

To **install ASHS** on your computer, follow the steps depicted in this tutorial :
https://sites.google.com/view/ashs-dox/local-ashs/installation?authuser=0

You can then **use it** following those instructions :
https://sites.google.com/view/ashs-dox/local-ashs/basic-usage?authuser=0

--------------------------

## Other tools

### How to use Anima ?

1) Download Anima binaries here :
https://anima.irisa.fr/downloads/

2) Unzip the archive.

3) Add Anima directory to your PATH
> export PATH=$PATH:/path_to_anima

4) You can use any function from Anima using anima\<Fct_name\> (help with "anima\<Fct_name\> -h")

### How to use MedINRIA (visualization) ?

Download it here :
https://med.inria.fr/