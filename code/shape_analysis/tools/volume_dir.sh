#!/bin/bash

input_dir=$1
output_dir=$2
volume_file=${output_dir}/volumes.txt

for filename in "${input_dir}"; do
    bash volume_single_file.sh "${input_dir}/${filename}" "${output_dir}" >>  "${volume_file}"
done