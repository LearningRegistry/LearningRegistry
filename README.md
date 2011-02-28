Installation on Turnkey Core (Ubuntu 10.04 LTS)
===============================================

## Configure apt sources ##

1. Edit the sources list       
>       sudo vim /etc/apt/source.list.d/sources.list
    
2. Add deb restrticted and multiverse, plus add deb-src for all:
>       deb http://us.archive.ubuntu.com/ubuntu lucid main universe restricted multiverse
>       deb http://us.archive.ubuntu.com/ubuntu lucid-updates main universe restricted multiverse
>       deb-src http://us.archive.ubuntu.com/ubuntu lucid main universe restricted multiverse
>       deb-src http://us.archive.ubuntu.com/ubuntu lucid-updates main universe restricted multiverse

3. Update apt sources
>       sudo apt-get update
    
    
## Install curl ##

1. Use apt-get to install curl
>       sudo apt-get install libcurl3 curl
    
    
## Install Python setup tools ##

1. Install Python easy_setup
>       sudo apt-get python-pkg-resources python-setuptools
    
    
## Install CouchDB ##

1. Build CouchDB dependencies
>       sudo apt-get build-dep couchdb

2. Install other dependencies
>       sudo apt-get install xulrunner-dev libicu-dev libcurl4-gnutls-dev libtool

3. Then create /etc/ld.so.conf.d/xulrunner.conf. 
>   a. To check what XULRunner version you have installed use xulrunner -v
>   b. Configure xulrunner
>       i. Edit the xulrunner.conf
>           sudo vi /etc/ld.so.conf.d/xulrunner.conf
>       ii. Add the following edits, replacing the x.x.x.x with your version number.
>           /usr/lib/xulrunner-x.x.x.x
>           /usr/lib/xulrunner-devel-x.x.x.x   
>   c. Update ldconfig
>       sudo /sbin/ldconfig

4. Download CouchDB from http://couchdb.apache.org/downloads.html.

5. Untar (decompress) the source file: 
>       tar -zxvf apache-couchdb-x.x.x.tar.gz

6. Change into the expanded directory: 
>       cd apache-couchdb-x.x.x

7. Install SpiderMonkey (see below)

8. Configure the build:     
>       LDFLAGS="$(pkg-config mozilla-js --libs-only-L)" CFLAGS="$(pkg-config mozilla-js --cflags)" ./configure
    
8. Build CouchDB:
>       make

9. Fix any errors

10. Install CouchDB to default location:
>       sudo make install

11. Add couchdb user account

12. change file ownership from root to couchdb user and adjust permissions
>       chown -R couchdb: /usr/local/var/{lib,log,run}/couchdb /usr/local/etc/couchdb
>       chmod 0770 /usr/local/var/{lib,log,run}/couchdb/
>       chmod 664 /usr/local/etc/couchdb/*.ini
>       chmod 775 /usr/local/etc/couchdb/*.d
    
13. install init script and start couchdb
>       cd /etc/init.d
>       ln -s /usr/local/etc/init.d/couchdb couchdb
>       /etc/init.d/couchdb start
        
14. configure couchdb to start on system start
>       update-rc.d couchdb defaults

15. Verify couchdb is running       
>       curl http://127.0.0.1:5984/

16. To accesses futon remotely and run tests, update the bind address in local.ini:    
>       sudo vim /usr/local/etc/couchdb/local.ini
>            [httpd]
>            ; Bind to all addresses
>            bind_address = 0.0.0.0

17. Restart couchdb
>       sudo service couchdb restart
    
    
## Install SpiderMonkey ##
1. Get one of the source tarballs from http://ftp.mozilla.org/pub/mozilla.org/js/ (1.7.0 or 1.8.0-rc1 will do).

2. Unpack the tarball. Note that once extracted the source are in the directory "js", without the expected version suffix.

3. Go to the js/src directory.
>       cd js/src

4. Build SpiderMonkey. There is no default Makefile, use Makefile.ref. The default build is debug, use BUILD_OPT=1 for an optimized build.
>       make BUILD_OPT=1 -f Makefile.ref

5. Install SpiderMonkey. Instead of "install" the target to use is "export". Instead of PREFIX the target directory is specified with JS_DIST.
>       sudo make BUILD_OPT=1 JS_DIST=/usr/local -f Makefile.ref export


## Install Python virtualenv and Pylons ##
1. Install virtualenv
>       sudo easy_install virtualenv

2. Create a user for learningregistry and su to user
>       su learningregistry

3. Create a directory for the virtualenv
>       mkdir virtualenv
>       cd virtualenv

4. Create virtualenv for LR
>       virtualenv --distribute lr
>       cd lr/bin/

5. Install LR Python deps
>       ./pip install pylons
>       ./pip install flup
>       ./pip install --upgrade couchdb

  
## Configure Nginx - Should be preinstalled on Ubuntu ##

1. Backup your original nginx.conf file
>       sudo cp /etc/nginx/nginx.conf /etc/nginx.conf.bak

2. Copy the ngnix.conf file from repository
>       sudo cp nginx.conf /etc/nginx/nginx.conf

## Start LR code ##

1. From your virtualenv directory start paster where */home/learningregistry/virtualenv/lr* is my path to virtualenv.
>       /home/learningregistry/virtualenv/lr/bin/paster server Ðreload  development.ini

2. You should now be able to navigate in your web browser.

            