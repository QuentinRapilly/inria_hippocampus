# Tools 

## Segmentation methods 
### How to use ASHS ?

Two methods exists :
* 1) An easy one : using ITK-SNAP GUI and cloud computing.
* 2) A more developped one : using ITK-SNAP in command line and calling cloud computing service.

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

To know every itksnap command just type :
`itksnap-wt`

I made a script (inspired from Quentin Duche's one) to process every segmentation of the MRI in our database available at `/code/ASHS/segmentation_auto`.

To use it :
`python3 /code/ASHS/segmentation_auto/automated_db_ASHS.py -i <path to img dir> -o <path to output storing>`

The output corresponding to labels is generally in file `/choosen_dir/sub-*/layer-002*.nii.gz`

To group every segmentation in files in the same dir, one can use the script `code/ASHS/segmentation_auto/group_seg_labels.py` that do this job :
`python3 code/ASHS/segmentation_auto/group_seg_labels.py -i <path to ASHS results> -o <path to where to store segs>`



--------------------------

## Other tools

### How to use Anima ?

1) Download Anima binaries here :
https://anima.irisa.fr/downloads/

2) Unzip the archive.

3) Add Anima directory to your PATH
`export PATH=$PATH:/path_to_anima`

4) You can use any function from Anima using `anima<Fct_name>` (help with "`anima<Fct_name> -h`")


#### Change label extension
Our labels are in format `label.mnc` and we need to convert them in `label.nii.gz`, to do it, we can use the following command from anima :
`animaConvertImage -i <mnc file> -o <output path> -s <reference space (an image given to set orientation, generally the image corresponding to labels)>`

#### Change ASHS segmentation resolution 
Once ASHS segmentations are downloaded they are not in the good resolution for 2 of the 3 dimension (they are up sampled during ASHS pipeline).

To down sample the labels :
`animaImageResolutionChanger -n <method to use [nearest, linear, bspline, sinc]> -i <input path> -o <output path>`

#### Select only some labels in a segmentation file
To keep only some labels on nifti images, one can use the following command to keep only the labels included between the two precised bounds.
`animaThrImage -u <Upper threshold value> -t <Threshold value> -i <Input image> -o <Output image>`

#### Create the .vtk from labels binaries
Create 3D meshes from labels binary files.

`animaIsoSurface -i <input binary image> -o <output surface>`

### How to use MedINRIA (visualization) ?

Download it here :
https://med.inria.fr/

For MedInria to work on Fedora distribution, replace this line in `bin/medInria_launcher.sh` :
* `export LD_LIBRARY_PATH=${MEDINRIA_DIR}/lib:${MEDINRIA_DIR}/plugins_legacy:$LD_LIBRARY_PATH`

by this one :
* `export LD_LIBRARY_PATH=${MEDINRIA_DIR}/lib:${MEDINRIA_DIR}/lib64:${MEDINRIA_DIR}/plugins_legacy:$LD_LIBRARY_PATH`
