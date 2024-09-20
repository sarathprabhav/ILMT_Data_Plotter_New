#!/bin/bash

# Remote server details
REMOTE_USER="ilmt"
REMOTE_HOST="172.20.2.233"
REMOTE_DIR="/ocs/archive"
LOCAL_DIR="./Data"

# Initial and final dates (format: YYYYMMDD)
initial_date="20240101"
final_date="20240331"

# Convert dates to seconds since epoch
start=$(date -d "$initial_date" +%s)
end=$(date -d "$final_date" +%s)

# Loop through each day in the range
for ((current_date=start; current_date<=end; current_date+=86400)); do
    # Format the current date as YYYYMMDD
    date=$(date -d "@$current_date" +"%Y%m%d")
    
    # Define the remote and local file paths
    REMOTE_FILE="$REMOTE_DIR/data_ic1_$date.tar"
    LOCAL_FILE="$LOCAL_DIR/data_ic1_$date.tar"
    
    # Copy the .tar file from the remote server
    scp "$REMOTE_USER@$REMOTE_HOST:$REMOTE_FILE" "$LOCAL_FILE"

    # Check if the copy was successful
    if [ $? -eq 0 ]; then
        echo "File $REMOTE_FILE copied successfully."

        # Extract the .tar file
        tar -xvf "$LOCAL_FILE" -C "$LOCAL_DIR"

        # Check if the extraction was successful
        if [ $? -eq 0 ]; then
            echo "File $LOCAL_FILE extracted successfully."

            # Delete the source .tar file
            rm "$LOCAL_FILE"
            echo "File $LOCAL_FILE deleted after extraction."
        else
            echo "Failed to extract $LOCAL_FILE."
        fi
    else
        echo "Failed to copy $REMOTE_FILE."
    fi
done
