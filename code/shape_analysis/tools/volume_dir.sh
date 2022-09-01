#!/bin/bash

input_dir=$1
output_dir=$2
volume_file=${output_dir}/volumes.txt

crt_path=pwd
path=$(dirname "$crt_path")

for filename in "${input_dir}"; do
    bash "${path}"volume_single_file.sh "${input_dir}/${filename}" "${output_dir}" >> "${volume_file}"
done