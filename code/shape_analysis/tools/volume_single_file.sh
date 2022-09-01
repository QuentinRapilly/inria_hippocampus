#!/bin/bash

output_dir=$1
img_dir=${output_dir}/tmp_img

input_file=$2

if [ ! -d "${img_dir}" ]; then
  mkdir -p "${img_dir}"
fi

crt_name=$(basename "$input_file")  
img_file=${img_dir}/"${crt_name%.*}".nii.gz

first_utils --meshToVol -m "${input_file}" -l 1 -o "${img_file}"
fslstats -V img_file
