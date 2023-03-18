#!/bin/bash

# specify the input and output file names
input_file="input.txt"
output_file="output.txt"

# loop through each line of the input file
while read -r line; do
  # check if the line contains one of the keywords
  if [[ $line =~ showthread|forum|forums|wiki|topic ]]; then
    echo "Skipping line: $line"
  else
    echo "Writing line: $line"
    # write the line to the output file
    echo "$line" >> "$output_file"
  fi
done < "$input_file"
