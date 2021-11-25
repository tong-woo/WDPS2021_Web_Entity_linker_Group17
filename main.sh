#!/bin/sh
echo "Processing webpages ..."
python3 main.py data/sample.warc.gz 
echo "Computing the scores ..."
python3 score.py data/sample_annotations.tsv sample_predictions.tsv