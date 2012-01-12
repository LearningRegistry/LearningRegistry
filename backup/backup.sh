#!/bin/bash
COUCHDIR=/var/lib/couchdb/1.0.1/
COUCHZIPDIR=~/couchzip
mkdir $COUCHZIPDIR
BACKUPDIR=(/var/log/learningregistry /mnt/couchdb/1.0.1 /var/log/nginx $COUCHZIPDIR)
BACKROOT=s3://lr.backups/$1/$2
for f in $COUCHDIR*.couch
do
    tar cjf $COUCHZIPDIR/${f:${#COUCHDIR}}.tar.bz2 $f
done
for d in ${BACKUPDIR[@]}
do
    s3cmd sync --recursive $d/* $BACKROOT$d/
done
rm -rf $COUCHZIPDIR
