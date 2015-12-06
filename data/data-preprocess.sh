#!/usr/bin/env bash

# download the alexa data
echo "Downloading alexa data..."
if [ ! -d "tmp" ]; then
  mkdir tmp
fi

cd tmp
curl -O https://s3.amazonaws.com/alexa-static/top-1m.csv.zip
unzip top-1m.csv.zip

echo "Processing csv..."
cut -d, -f1 --complement top-1m.csv > no-ranknum-top-1m.txt

cd ..
# First time prepare data
if [ ! -f "base.txt" ]; then
  # base
  cp tmp/no-ranknum-top-1m.txt base.txt
  # append
  touch append.txt
# Update data
else
  # find new domain and add to append.txt
  sort base.txt base.txt append.txt tmp/no-ranknum-top-1m.txt | uniq -u >> append.txt
fi

