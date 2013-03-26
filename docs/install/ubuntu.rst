==============================
LR Install on Ubuntu 12.04 LTS
==============================

The following is a series of instructions designed to assist in the configuration of the Learning Registry Node software.


-------
Gotchas
-------

While we try to keep documentation up-to-date. Some dependencies update more frequently than these instructions. The following are some
commonly known stumbling blocks:

* CouchDB with BrowserID plugin 
    - the BrowserID integrates with `Mozilla's Persona <https://developer.mozilla.org/en-US/docs/Persona>`_ whose protocol is still developmental, however relatively stable.  Revisions to the protocol have often required configuration changes to the updated plugin. Please refer to the `developer's site <https://github.com/iriscouch/browserid_couchdb>`_ for more information
                              

-----
Steps
-----

1. (optional) Install SSH server so we can remote ssh into server so copy/paste works.
--------------------------------------------------------------------------------------

::

    sudo apt-get install openssh-server


2. Update and Upgrade system
----------------------------

::

    sudo apt-get update
    sudo apt-get upgrade


3. Install system dependencies
------------------------------

::

    sudo apt-get install flex dctrl-tools libsctp-dev ed zlib1g-dev
    sudo apt-get install libxslt1-dev automake make ruby libtool g++
    sudo apt-get install zip libcap2-bin
    sudo apt-get install python-dev python-setuptools python-virtualenv
    sudo apt-get install nginx libyajl1 git-core curl rake swig vim


4. Make Users for CouchDB and Learning Registry
-----------------------------------------------

::

    sudo adduser couchdb
    sudo adduser learnreg


5. Build CouchDB 1.2.0 with some additional plugins
---------------------------------------------------

::

    sudo mkdir /opt/couchdb
    sudo chown couchdb:couchdb /opt/couchdb
    sudo su - couchdb
    git clone git://github.com/jimklo/build-couchdb        ## TODO move to LearningRegistry
    cd build-couchdb
    git submodule init
    git submodule update
    rake install=/opt/couchdb/1.2.0 git="git://github.com/apache/couchdb tags/1.2.0" plugins="git://github.com/iriscouch/browserid_couchdb origin/master,git://github.com/couchbase/geocouch origin/couchdb1.2.x"

.. note::

    1. Ensure that the rake command uses the correct git path and branch/tag for the plugins parameter.
    2. At the time of this writing, ``git://github.com/iriscouch/build-couchdb`` had reliablity issues for Ubuntu 12.04, which may be fixed. If the listed location in the source does not work, try the original.
    3. You may omit the geocouch plugin as it not currently utilized, but may have planned future use.  It may be added in the future when needed.  If you wish to omit, remove ``git://github.com/couchbase/geocouch origin/couchdb1.2.x`` from the rake command

While CouchDB builds (it takes a long time), you can log into a separate session and begin installing Learning Registry at 5b


6. Install Learning Registry code
---------------------------------

Clone from GitHub:

::

    sudo su - learnreg
    git clone git://github.com/LearningRegistry/LearningRegistry


.. note::
  
    If you require a different branch other than head, please refer to the git documentation for checking out an alternate version


Create the Python virtualenv and install uwsgi and the node software:

::

    virtualenv --no-site-packages env
    . env/bin/activate
    pip install uwsgi
    pip install -e ./LearningRegistry/LR/




7. Configure CouchDB
--------------------

::

    cd /opt/couchdb/
    ln -s ./1.2.0 current
    cd 1.2.0
    vim env.sh

Within the main() function, after the last dir_to_path line (about line 40) add the following by using arrow keys to navigate, then press "<ESC> o" and type:

::

    export ERL_FLAGS="-pa /opt/couchdb/1.2.0/lib/couchdb/plugins/geocouch/ebin /opt/couchdb/1.2.0/lib/couchdb/plugins/browserid_couchdb/ebin"

Save and exit by pressing "<ESC> :wq"

::

    vim etc/init.d/couchdb


Navigate using the arrow keys after the line with ``LSB_LIBRARY=...`` (around line 35), add the following line by pressing "<ESC> o" and type:

::

    export ERL_FLAGS="-pa /opt/couchdb/1.2.0/lib/couchdb/plugins/geocouch/ebin /opt/couchdb/1.2.0/lib/couchdb/plugins/browserid_couchdb/ebin"


Save and exit by pressing "<ESC> :wq"

::

    vim etc/couchdb/local.ini


Navigate to the end of the file and locate the [admins] section. Create an admin user (equivalent to a DBA) by pressing "<ESC> o" and type below ``[admins]``:

::

    [admins]
    admin = password


Substituting the password of your choice. The password will be hashed after startup. Save and exit by pressing "<ESC> :wq".

Try starting couchdb:

::

    /opt/couchdb/current/etc/init.d/couchdb start
    curl http://localhost:5984

You should see:

::

    {"couchdb":"Welcome","version":"1.2.0"}

Next let's make sure we can authenticate:

::

    curl 'http://admin:password@localhost:5984/_session'

We should get a response like this: 

::

    {"ok":true,"userCtx":{"name":"admin","roles":["_admin"]},"info":{"authentication_db":"_users","authentication_handlers":["oauth","cookie","default"],"authenticated":"default"}}

Next we want to make sure our plugin got installed correctly:

::

    curl http://localhost:5984/_browserid/main.js

You should see the contents of a Javascript code returned.  If you see a single line that indicates an error, read on. A common problem is to use the wrong plugin url which produces a plugin directories that end in ".git". Check in ``/opt/couchdb/1.2.0/lib/couchdb/plugins``, and if you see any directories that end in ".git" (ie browserid_couchdb.git or geocouch.git) this is incorrect and plugins will need to be rebuilt. Recheck the 'rake' command you used and try rebuilding. Ensure that the git URI's for the plugins parameters do NOT end in ".git" (however they should begin with "git://").

Stop couchdb for now and exit couchdb user shell:

::

    /opt/couchdb/current/etc/init.d/couchdb stop
    exit

Next configure couchdb basic management and start couchdb again:

::

    sudo ln -s /opt/couchdb/current/etc/init.d/couchdb /etc/init.d/couchdb
    sudo ln -s /opt/couchdb/current/etc/logrotate.d/couchdb /etc/logrotate.d/couchdb
    sudo update-rc.d couchdb defaults
    sudo service couchdb start

We are done with configuration of CouchDB for now, you can refer to ``/opt/couchdb/current/etc/couchdb/local.ini`` and ``/opt/couchdb/current/etc/couchdb/default.ini`` for further configurations options as well as the CouchDB wiki: http://wiki.apache.org/couchdb/

8. Configure GPG, NGINX, and LR
-------------------------------

If you do not have an existing GPG Keypair for the node, create a new one via:

::

    gpg --gen-key

After doing this, take note of the key id, which is the last 16 characters of the key fingerprint.  You can get this by doing:


::

    gpg --list-secret-keys --fingerprint
    
    /home/learnreg/.gnupg/secring.gpg
    ---------------------------------
    sec   2048R/017491D1 2012-06-15
          Key fingerprint = B418 70F5 A781 24F2 5AE5  243D E33C DDFF 0174 91D1
    uid                  Jim Klo (Resource Data Signing Key) <jim.klo@sri.com>


"E33CDDFF017491D1" is the key ID from the example above.

::

    cd /home/learnreg/LearningRegistry/config
    python ./setup_node.py

Follow the prompts.  Be sure to enable OAuth and Node Signing. Tip: Login a separate shell if you need to investigate some of the questions (path to NGINX, certs, etc)

In a separate shell (one that has sudo privleges) do the following:

::

    sudo rm /etc/nginx/sites-enabled/default
    sudo cp /home/learnreg/LearningRegistry/config/learningregistry.conf /etc/nginx/sites-available/
    sudo ln -s /etc/nginx/sites-available/learningregistry.conf  /etc/nginx/sites-enabled/learningregistry.conf
    sudo cp -r /home/learnreg/LearningRegistry/etc/nginx/conf.d/* /etc/nginx/conf.d/
    sudo cp -r /home/learnreg/LearningRegistry/etc/nginx/learningregistry_cgi /etc/nginx/learningregistry_cgi
    sudo service nginx restart


9. Start LR for the first time
------------------------------

Switch back to the learnreg user account:

::

    cd /home/learnreg
    . env/bin/activate
    uwsgi --ini-paste ./LearningRegistry/LR/development.ini -H ./env


In a browser, you should be able to load the 'home page' of the node
by going to the URL. I used the external IP as my node address so:

::

    http://192.168.96.134

You should also try the following:

::

    http://192.168.96.134/status
    http://192.168.96.134/services
    http://192.168.96.134/destination
    http://192.168.96.134/obtain
    http://192.168.96.134/harvest/listrecords
    http://192.168.96.134/pubkey

Since your node is empty, don't expect any data, but there shouldn't
be any errors.


You should also verify that you can reach the user registration for node signing, this should redirect to the login interface.  

::

    http://192.168.96.134/auth
    


.. note::
    
    If you have problems with accessing the registration page, check the NGINX configuration file to ensure it is appropriate for your environment.  The configuration should be located ``/etc/nginx/sites-enabled/learningregistry.conf``.


Switch back to the shell that's running uwsgi, and type "<control> c", to stop
the process




10. Configure LR As a service
-----------------------------

::

    sudo su - learnreg cd /home/learnreg/LearningRegistry/config .
    ../../env/bin/activate python ./service\_util.py exit sudo cp
    /home/learnreg/LearningRegistry/config/learningregistry.sh
    /etc/init.d/learningregistry sudo chmod +x
    /etc/init.d/learningregistry sudo update-rc.d learningregistry
    defaults sudo service learningregistry start sudo cp
    /home/learnreg/LearningRegistry/etc/logrotate.d/learningregistry
    /etc/logrotate.d/


11. Learning Registry Node Should be up and running
---------------------------------------------------


