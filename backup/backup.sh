#!/bin/bash
BACKUPDIR=(/var/log/learningregistry /mnt/couchdb/1.0.2 /var/log/nginx)
BACKROOT=s3://lr.backups/$1/$2
for d in ${BACKUPDIR[@]}
do
    s3cmd sync --recursive $d/* $BACKROOT$d/
done
