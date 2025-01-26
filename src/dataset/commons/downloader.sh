#!/bin/bash

url="https://ks.echr.coe.int/documents/d/echr-ks/guide_art_4_ara"

output_path="Guide_Art_2_ARA_Downloaded.pdf"

wget -O "$output_path" "$url"

if [ $? -eq 0 ]; then
    echo "PDF downloaded successfully and saved as $output_path"
else
    echo "Failed to download PDF"
fi
