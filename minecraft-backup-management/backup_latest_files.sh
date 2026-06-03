#!/bin/bash

# Define the directory to search and the destination directory
SEARCH_DIR="./"
DEST_DIR="./+ Most Recent Backups"

# Find all files matching the pattern with the date part
files=$(find "$SEARCH_DIR" -type f -name "*.zip" | grep -E '/[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}_.+\.zip$')

# Initialize variables to keep track of the most recent file
most_recent_file=""
most_recent_date=0

# Loop through the found files
for file in $files; do
    # Extract the date part of the filename
    filename=$(basename "$file")
    date_part=$(echo "$filename" | grep -oP '^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}')

    # Convert the date part to a timestamp for comparison
    file_date=$(date -d "${date_part//[-_]/ }" +%s)

    # Update the most recent file if this one is newer
    if [[ $file_date -gt $most_recent_date ]]; then
        most_recent_date=$file_date
        most_recent_file=$file
    fi
done

# Copy the most recent file to the destination directory
if [[ -n $most_recent_file ]]; then
    cp "$most_recent_file" "$DEST_DIR"
    echo "Copied $most_recent_file to $DEST_DIR"
else
    echo "No matching files found."
fi
