# Automated volumetry and regional thickness analysis of hippocampal subfields and medial temporal cortical structures in Mild Cognitive Impairement (MCI) - Paul A. Yushkevich

No manual initialization ($\neq$ previous work, Yushkevich 2010).

## Introduction 

Focus on the __subfields__ of hippocampus recently.
The objective is to segment the hippocampus but also its subfields and the surrounding structures :
* enthorinal cortex (ERC)
* perirhinal cortex (PRC)
* parahippocampal cortex (PHC)

Two kinds of data : 
* "routine" : full brain MRI in low resolution (commonly acquired MRI)
* "dedicated" : higher definition MRI focused on the hippocampus

On routine, hippocampus looks homogeneous making really hard to identify subfields => No manual techniques existing. 

Computationnal methods :
* template-based : segments the whole hippocampus $\rightarrow$ projects it into a particular space $\rightarrow$ segments the subfields using statistical approaches and ROI.
* automatic segmentation (tested and validated with "dedicated" MRI but commonly used with "routine").

Protocols to manually segment hippocampus on "dedicated" exist but are very time consumming.
Only a few slices : a lot of the hippocampus isn't represented => weak representation.

Multi atlas segmentation and ML technics.

Two pipelines : 
* a training one
* a segmentation one

In the article, mainly using T2w MRI (but today other implementations using T1w).

The segmentation pipeline detects the hippocampus and the surrounding regions then projects them in a particular space to make a statistical study to segment subfields.
Evaluate the thikness of the hippampus (better than the volume).

-------------------------------

## Materials and methods

### Subjects

90 subjects (45 with aMCI ~ kind of amnesia (forget appointment, conversation), 45 healthy)

### Manual segmentation

29 MRI were manually segmented (15 healthy, 14 aMCI) => called the "atlas subset".

12 subjects (6 healthy, 6 aMCI) were resegmented => called the "reliability subset". For a half : only the left part segmented ; for the other half : right part.

----------------------------------

## ASHS algorithm and software

### ASHS Core Algorithm

> **Joint label fusion** (JLF) : 
Multi atlas image segmentation algorithm. Performs deformable registration between the target image and the set of labeled atlas images.
For each voxel in the target image, each atlas image gives a segmentation label, then weighted voting to get the strong segmentation.
*To understand how weight are computed, see the paper on JLF algorithm. Shortly : atlas with the higher similarity to the currently traited MRI have the bigger weigths.*

> **Corrective Learning** (CL) :
Detects misslabeled voxels and try to correct them.
Using Adaboost Classifier

### ASHS training pipeline

Goal : obtaining a dataset of atlases (that will be reused for segmentation).

Input : T2w and T1w MRI for the subjects whom T2w was manually labelled.

Algorithm :
* 1) T1w and T2w are aligned.
* 2) T1w MRI are deformed to lie in a unbiased template.
* 3) Creation of masks for each subject and a global mask covering the hippocampus for the whole dataset which is used to compute the ROI.
* 4) Training of the CL classifiers with "Leave one out" cross validation technics.

### ASHS segmentation pipeline

Input : T1w and T2w MRI.

Algorithm :
* 1) T1w and T2w are aligned.
* 2) T1w MRI is deformed to lie in the same unbiased template than the training dataset.
* 3) JLF algorithm is applied using atlases obtained in the training pipeline.
* 4) CL classifiers try to correct the previouly computed labels of step 3.
* 5) Steps 3. and 4. are repeated severall times using the corrected weigths in input to improve the segmentation.

### Evaluation of ASHS accuracy using cross validation

Relative overlap computed using Dice Similarity and Generalized Dice Similarity (Cf Manjon.md).

Overlap for :
* the whole hippocampus (every substructures) ~ 78%
* the substructures : from 55% (for small fields such as CA2 and CA3) to 83% (DG).

Few differences between aMCI group and NC group but not a lot.

### Measurements of volume 

Volumetry measurements are done for the hippocampus but also for the subfields.

----------------------------------------


## Discussion

Subfields segmentation is criticized [van Strien] (for example because difference between CA1 and CA2 is based only on difference of density of pyramidal neurones and that can't be detected on MRI).
But even if methods such as the one depicted in this paper don't show the anatomical reality they can still be useful to determine biomarkers and understand diseases.
The problems remains for every small brain structure, not only hippocampus. 

Advantages of computer driven methods : reproductible and easily adaptable on large dataset whereas manually segmentation can't.

-------------------------

## ASHS performance compared to other methods

Competitive with other methods (~75% max for other methods at the time the article was published against 80% for ASHS).
But some other methods only use T1w and can then be applied to larger cases of study.

-------------------------

## Effect of aMCI on the hippocampal region

Confirm previous studies : smaller CA1 and subiculum, unusual CA1-CA2 transition for aMCI subjects => hot spots for loss of thickness in aMCI.