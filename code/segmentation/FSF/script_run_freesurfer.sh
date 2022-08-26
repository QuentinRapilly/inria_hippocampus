#!/bin/bash

# Load paths
#source ../config/.env
#source "${aneravimm_dev_dir}"/scripts/rs_fmri/select_subjects.sh

adni_logs_dir = "/nfs/nas4/empenn/empenn/qrapilly/ADNI/logs/"

for filename in `ls /nfs/nas4/empenn/empenn/qrapilly/ADNI/imgs/`; do 

  su_id ="${filename%.*}";

  oarsub \
        -O "${adni_logs_dir}"/freesurfer/"${su_id}".%jobid%.output \
        -E "${adni_logs_dir}"/freesurfer/"${su_id}".%jobid%.error \
        -l /nodes=1/core=4,walltime=12:00:00 \
        "bash single_subject_run_freesurfer.sh $su_id"

done
