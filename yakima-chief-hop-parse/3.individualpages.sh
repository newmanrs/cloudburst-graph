#!/bin/zsh

mkdir -p pages
i=2 #Start page 2
while IFS= read -r line; do
    printf '%s, Page %s \n' "$line" "$i"
    outfile=pages/${line}.txt
    outfile=$(echo $outfile | sed -e "s/ /_/g")
    echo $outfile
    pdftotext -layout -enc UTF-8 -f $i -l $i yakchiefhops.pdf $outfile
    #echo Page $i
    i=$(($i+1))

done < hopnames.txt


