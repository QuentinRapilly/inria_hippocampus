adni_dir='/nfs/nas4/empenn/empenn/qrapilly/ADNI'

# For being able to load modules
. /etc/profile.d/modules.sh

set -xv

# Load module freesurfer
module load neurinfo/freesurfer/7.2.0
source $FREESURFER_HOME/SetUpFreeSurfer.sh

su_id=$1

#Before INPUT_DIR=${adni_dir}/bids/sub-${su_id}
INPUT_DIR=${adni_dir}/imgs

# Convert directory
#Before FREESURFER_DIR=${aneravimm_dir}/freesurfer
FREESURFER_DIR=${adni_dir}/freesurfer
SUBJECTS_DIR=${FREESURFER_DIR}/subjects

# Specific to subject
SU_DIR=${SUBJECTS_DIR}/${su_id}
ORIG_DIR=${SU_DIR}/mri/orig


if [ ! -d "${ORIG_DIR}" ]; then
  mkdir -p "${ORIG_DIR}"
fi

# Correspond to T1 path (in nii format)
mprage=${INPUT_DIR}/${su_id}.nii

# Convert MPRAGE file to .mgz
mri_convert "${mprage}" "${ORIG_DIR}"/001.mgz

echo "Running Freesurfer..."
cd "${SUBJECTS_DIR}"
recon-all \
  -sd "${SUBJECTS_DIR}" \
  -s ${su_id} \
  -all \
  -openmp 4 \
  -mail quentin.rapilly@inria.fr

#  echo "Convert output..."
#  ATLASES="wmparc aparc+aseg aparc.a2009s+aseg"
#  for ATLAS in $ATLASES
#  do
#    mri_label2vol \
#      --seg ${SUBJECTS_DIR}/freesurfer/mri/${ATLAS}.mgz \
#      --temp ${SUBJECTS_DIR}/freesurfer/mri/rawavg.mgz \
#      --o ${SUBJECTS_DIR}/fs_${ATLAS}.nii.gz \
#      --regheader ${SUBJECTS_DIR}/freesurfer/mri/${ATLAS}.mgz
#  done

