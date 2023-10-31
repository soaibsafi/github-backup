#!/bin/bash

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  touch .env
fi

echo "GITHUB_ACCESS_TOKEN=$GITHUB_ACCESS_TOKEN" > .env
echo "BACKUP_DIR=$BACKUP_DIR" >> .env


while true
  do python3 github_backup/backup.py -b -e .env 
  sleep $BACKUP_INTERVAL
done