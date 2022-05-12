# User guide

> The following file depicts how to use the major part of the codes I implemented during my internship.

> I developped those codes using **Python 3.6+**. The required packages are **numpy** and sometimes **nibabel**. If any other package is required, that should be depicted below.

For any further question, do not hesitate to ask me by email.


----------------------------------------

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
2. connect to a google account using command :
`itksnap-wt -dss-auth https://dss.itksnap.org` and following the returned link
3. you can now use ITK-SNAP cloud services in command line

To know every itksnap command just type :
`itksnap-wt`

I made a script (inspired from Quentin Duche's one) to process every segmentation of the MRI in our database available at `/code/segmentation/ASHS/`.

To use it :
`python3 /code/segmentation/ASHS/automated_db_ASHS.py -i <path to img dir> -o <path to output storing>`

The output corresponding to labels is generally in file `/choosen_dir/sub-*/layer-002*.nii.gz`

To group every segmentation files in the same dir, one can use the script `code/segmentation/ASHS/group_seg_labels.py` that do this job :
`python3 code/segmentation/ASHS/group_seg_labels.py -i <path to ASHS results> -o <path to where to store segs>`

### How to use the CNN-Based Method

TODO : terminer l'implémentation et décrire son fonctionnement.

--------------------------

## Dealing with the data (images and labels)

### How to use Anima ?

1) Download Anima binaries here :
https://anima.irisa.fr/downloads/

2) Unzip the archive.

3) Add Anima directory to your PATH
`export PATH=$PATH:/path_to_anima`

4) You can use any function from Anima using `anima<Fct_name>` (help with "`anima<Fct_name> -h`")


### Change label extension
Our labels are in format `label.mnc` and we need to convert them in `label.nii.gz`, to do it, we can use the following command from anima :
`animaConvertImage -i <mnc file> -o <output path> -m <model space (an image given to set orientation, generally the image corresponding to labels)>`

A **script** does it for every files in a dir :
`python3 /code/label_tools/mnc_to_nifti.py -i <path to mnc files> -o <path to where to store nifti files>`

### Change ASHS segmentation resolution 
Once ASHS segmentations are downloaded they are not in the good resolution for 2 of the 3 dimension (they are up sampled during ASHS pipeline).

To down sample the labels :
`animaImageResolutionChanger -n <method to use [nearest, linear, bspline, sinc]> -i <input path> -o <output path>`

### Select only some labels in a segmentation file (a)
To keep only some labels on nifti images, one can use the following command to keep only the labels included between the two precised bounds.
`animaThrImage -u <Upper threshold value> -t <Threshold value> -i <Input image> -o <Output image>`

### Create the .vtk from labels binaries (b)
Create 3D meshes from labels binary files.

`animaIsoSurface -i <input binary image> -o <output surface>`

A script creates temporary binaries (step (a)) and uses them to create .vtk files from labels mask (step (b)) :
`python3 code/label_tools/labels_to_vtk.py -i <input files> -o <out files dir> -m <lower bound to select labels> -M <upper bound to select labels>`


--------------------------------------------------

## Shape analysis

### How to use Deformetrica ?

Deformetrica is a module giving access to severall tools for shape analysis.

It is now a Python package that can be downloaded using pip :
`pip install deformetrica`


I really recommand you to use conda to deal with Deformetrica, it was made to run on Linux/MacOS and it is much more convenient to install it using Anaconda.
Use this command to create a dedicated environment :
`conda create -n deformetrica python=3.8 numpy && source activate deformetrica`
You can then use the pip command in the dedicated env.

> It is really easy if you work on Linux. I also used it on Windows. To do it, install the **WSL** (Windows Subsystem for Linux) that allows to use linux softwares on Windows, then install a version of conda dedicated to Linux in a WSL shell. You will then be able to use the previous command.

A wiki dedicated to deformetrica is available at the following adress : [Deformetrica wiki](https://gitlab.com/icm-institute/aramislab/deformetrica/-/wikis/home).

### Using the Python API

Deformetrica was written in Python but was not written in order to be functions called in other scripts. It was written to be called in command line following the use cases depicted in the wiki introduced before.
For more complicated use case, one can want to do severall call to some of the methods in a row.

To do so, let's follow the code bellow that call the Deformetrica API : 
```
import deformetrica as dfca

deformetrica = dfca.Deformetrica(output_dir='output', verbosity='INFO')

dataset_specifications = {dict containing every information required for\
    the dataset_specifications (ex : 'deformable_object_type' : 'polyline')}
template_specifications = {dict containing every information required for\
    the template_specifications}
estimator_options = {dict containing the estimator options}
model_options = {dict containing the model options}

model = deformetrica.<method_to_use>(template_specifications, dataset_specifications,\
    estimator_options, model_options)
```


### Using the _registration_ method

This methods allows to get the trajectory starting from a given shape and reaching an another.
The documentation for this method is given [here](https://gitlab.com/icm-institute/aramislab/deformetrica/-/wikis/2_tutorials/2.1_registration).

> **model.xml**
In our case, we use `SurfaceMesh` instead of `Image` type for the `deformable-object-type` parameter.

To use it from the Python API, here is the description of the parameter and the name of the method :

```
import deformetrica as dfca

df = dfca.Deformetrica(output_dir='output', verbosity='INFO')

df.estimate_registration(self, template_specifications,\ 
    dataset_specifications, model_options={}, estimator_options={}, write_output=True)
```
_Estimates the best possible deformation between two sets of objects.
Note: A registration is a particular case of the deterministic atlas application, with a fixed template object._
1. _(dict)_ **template_specifications**: Dictionary containing the description of the task that is to be performed (such as estimating a registration, an atlas, ...) as well as some hyper-parameters for the objects and the deformations used.
2. _(dict)_ **dataset_specifications**: Dictionary containing the paths to the input objects from which a statistical model will be estimated.
3. _(dict)_ **model_options**: Dictionary containing details about the model that is to be run.
4. _(dict)_ **estimator_options**: Dictionary containing details about the optimization method. This will be passed to the optimizer's constructor.
5. _(bool)_ **write_output**: Boolean that defines if output files will be written to disk.

### Using the _shooting_ method

This methods allows to get a new shape along a given trajectory (initial point and momenta).
The documentation for this method is given [here](https://gitlab.com/icm-institute/aramislab/deformetrica/-/wikis/2_tutorials/2.6_shooting).

To use it from the Python API, here is the description of the parameter and the name of the method :

```
df.compute_shooting(self, template_specifications, model_options={})
```
_If control points and momenta corresponding to a deformation have been obtained, it is possible to shoot the corresponding deformation of obtain the flow of a shape under this deformation._
1. _(dict)_ **template_specifications**: Dictionary containing the description of the task that is to be performed (such as estimating a registration, an atlas, ...) as well as some hyper-parameters for the objects and the deformations used.
2. _(dict)_ **model_options**: Dictionary containing details about the model that is to be run.

### Iterativ barycentre algorithm

Considering we have $N$ shapes (hippocampus or subfields in our case) we want to compute the mean shape of our dataset of shapes.
To do it, one could use the method given by Deformetrica but it is very time consuming.

We then propose an alternativ method computing iteratively barycentre of a subset of shapes :

0. Using Deformetrica, we compute the barycentre of two shapes. To do it we firstly use the _registration_ method to get the trajectory from one shape $s_1$ to the other $s_2$ (giving a trajectory $\gamma_0$ such that $\gamma_0(0)=s_1$ and $\gamma_0(1)=s_2$).
Then we take the shape at the middle of the trajectory using method _shooting_. Giving a first mean shape $\mu = \gamma_0(\frac{1}{2})$ (and we set the value of the weight $w=2$). 
1. We pick one of the non processed shape $s_i$ remaining in the dataset. Then we compute the _registration_ of $\mu$ to $s_i$ giving $\gamma_i$. 
2. Update the weight and the mean : $w \leftarrow w + 1$ ; $\mu \leftarrow \gamma_i(\frac{1}{w})$.
3. Return to step 1. if some shapes remain unprocessed.


This algorithm is available in the script `shape_analysis/iterativ_barycentre.py` and can be called using the following command (keep in mind that you should be in an conda env where Deformetrica has been installed) :
`python3 code/shape_analysis\iterativ_barycentre.py -i <dir containing the .vtk shapes> -o <dir to write the output file> -c [optionnal] <config file for the config dict>` 


--------------------------------------------------

## Visualization

### How to use MedINRIA (visualization) ?

Download it here :
https://med.inria.fr/

For MedInria to work on Fedora distribution, replace this line in `bin/medInria_launcher.sh` :
* `export LD_LIBRARY_PATH=${MEDINRIA_DIR}/lib:${MEDINRIA_DIR}/plugins_legacy:$LD_LIBRARY_PATH`

by this one :
* `export LD_LIBRARY_PATH=${MEDINRIA_DIR}/lib:${MEDINRIA_DIR}/lib64:${MEDINRIA_DIR}/plugins_legacy:$LD_LIBRARY_PATH`
