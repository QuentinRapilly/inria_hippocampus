# HIPS - A new hippocampus subfield segmentation method (Romero)

## Introduction

Common speech on hippocampus (interest of segmentation, division CA1-4, DG ...)

Segmenting the subparts is a real challenge.

Lack of labelled data.

This method was initially developped for high resolution T1w and T2w MRIs but can also work on standard resolution MRI with only T1w (or only T2w).

-------------------------------------------------

## Materials and methods 

### Data 

> **Kulaga-Yoskivitz** dataset : 25 manually segmented subjects (containing T1w and T2w observations).
Segmentations divide the hippocampus in 3 parts CA1-3, DG-CA4, Subiculim.

> **Winterburn** dataset : 5 manually segmented subjects with HR T1w and T2w MRIs.

### Proposed method

> **Preprocessing** :
Objective is to locate images in a common intensity and coordinate space (to better match library subjects with new cases of study).
Steps : denoising, moving images in the Montreal Neurogical Institute (MNI) space (which correspond to a standard way to crop MRI), intensity normalization, images are then cropped around HC area (to reduce memory required).
For low resolution MRIs, data are firstly up-sampled.

> **Library construction** :
Atlas library created by applying the previous steps to a learning dataset.
Left right flip for data augmentation.

> **Labeling** : 
MOPAL (Multi-contrast optimized PatchMatch) technic : non local patch-based fusion technique. Patches of the subject to be segmented are compared with patches of the training library to look for similar paterns.
The "probability" (not really a proba before a softmax is done over labels) for voxel $i$ to have label $l$ is given by $v_l(x_i) = \frac{\sum_{i=1}^N\sum_{j\in V_i} w(x_i,x_{s,j}).y_{s,j}^{(l)}}{\sum_{i=1}^N\sum_{j\in V_i} w(x_i,x_{s,j})}$
Where $w(x_i,x_{s,j})$ is the patch similarity between the patch centered in $x_i$ in the processed subject and the patch centered in $x_j$ in the reference atlas $s$ (more details in paper).
$y_{s,j}^{(l)} = 1$ if the expert gave label $l$ to voxel $j$ the ref atlas $s$ ($y_{s,j}^{(l)}=0$ instead).

BUT : Computing patch comparision $w(x_i,x_{s,j}) = e^{-||P(x_i)-P(x_{s,j})||_2^2/h^2}$ is time consuming.

Method to solve this issue $\Rightarrow$ Approximated Nearest Neighbor Field (ANNF).
Let $A$ be the processed image and $B$ an image from the atlas dataset.
1) Random correspondances are made between patches from $A$ and $B$.
2) If a patch $x$ from $A$ is similar to $y$ a patch from $B$, then $x'$ a patch from $A$ close to $x$ will probably be similar to $y'$ close to $y$ in $B$. We then update the correspondances.
3) Random local steps are made to avoid local minima.
Steps 2 and 3 are repeated iteratively.


> **Multi scale label fusion** :
Label are predicted at several scales (several resolutions). And then averaged with weights :
$p(l) = \alpha(l).p_1(l)+(1-\alpha(l)).p_2(l)$
with $p(l)$ the probability map of label $l$. Weights $\alpha$ are optimized by GD.

> **Multi-contrast patch similarity** :
If several types of MRI are used for the segmentation (ex : T1w and T2w). A particular similarity measure is introduced to take into account multiple channels. 
(**But that is not our use case**)

> **Systematic error correction** : 
Adaboost classifiers are learned to correct systematic errors.
Neural networks in cascad, one has to learn the error from the previous one.

------------------------------------

## Experiments and results

The method was tested using cross-validation on both datasets.

Tests were made with and without Error Corrector, with high and low resolution.

Comparisions with ASHS, SurfPatch, MAGeT.

Improvements in both cases.