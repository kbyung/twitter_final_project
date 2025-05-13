#!/bin/sh

# Default max_rows value
max_rows=""

# Collect all files
files=$(find data/*)

echo 'load normalized'

# Check for -m flag
if [ "$1" = "-m" ]; then
    # Check if a value is provided for -m
    if [ -n "$2" ]; then
        max_rows="$2"
    else
        echo "Error: -m flag requires a numerical argument"
        exit 1
    fi
fi

# Execute the parallel command
if [ -n "$max_rows" ]; then
    num_files=$(find data/* | wc -l)

    rows_per_file=$((max_rows/ $num_files))

    time parallel python3 load_tweets.py \
        --db "postgresql://hello_flask:hello_flask@localhost:12347/hello_flask_dev" \
        --max_rows "$rows_per_file" \
        --inputs {} ::: $files
else
    time parallel python3 load_tweets.py \
        --db "postgresql://hello_flask:hello_flask@localhost:12347/hello_flask_dev" \
        --inputs {} ::: $files
fi

