# Tools 

## Segmentation methods 
### How to use ASHS ?

Two methods exists :
* 1) An easy one : using ITK-SNAP and cloud computing.
* 2) A more developped one : downloading ASHS codes and running it on your own device.

#### Easy method : ITK-SNAP Cloud and GUI

1) You should start by downloading ITK-SNAP 3.8 or later (http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.SNAP3)

2) Follow the instructions given on this guide : https://sites.google.com/view/ashs-dox/cloud-ashs/cloud-ashs-for-t1-mri?authuser=0

#### Developped method : ITK-SNAP Cloud in command line (to process severall segmentations)

When ITK-SNAP is downloaded, in ITK-SNAP directory you will find to files :
* itksnap : to launch itk-snap GUI and used the previous method.
* itksnap-wt : that allows to use ITK-SNAP services in command line.

1. add itksnap to your path : 
`export PATH=$PATH:/path_to_itksnap_directory`
close the terminal to update the path
2. connect to a google account :
`itksnap-wt -dss-auth https://dss.itksnap.org`
3. you can now use ITK-SNAP cloud services in command line

I made a script (inspired from Quentin Duche's one) to process every segmentation of the MRI in our database available at `\code\ASHS\segmentation_auto`.



--------------------------

## Other tools

### How to use Anima ?

1) Download Anima binaries here :
https://anima.irisa.fr/downloads/

2) Unzip the archive.

3) Add Anima directory to your PATH
`export PATH=$PATH:/path_to_anima`

4) You can use any function from Anima using anima\<Fct_name\> (help with "anima\<Fct_name\> -h")

### How to use MedINRIA (visualization) ?

Download it here :
https://med.inria.fr/