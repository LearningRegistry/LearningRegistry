************************************
Learning Registry Distribution Guide
************************************


Configure a LR Node for Distribution
====================================

* When setting up a node, answer ``T`` for the question, ``Is the node "open"?``
  
* To run the distribution service for your node on-demand, hit the URL directly *locally* on the node:
	
	.. code-block:: bash
	
	    curl -XPOST -H "Content-Type:application/json" http://localhost/distribute

* To automate the service add a cron job to the root user on the node. On the LR public nodes it runs hourly with the following in the root user’s crontab:

	.. code-block:: bash
	
	    @hourly curl -XPOST -H "Content-Type:application/json" http://localhost/distribute

* Other node admins register to have your node distribute to them at ``http://<yourNodesPublicAddress>/register`` 

    - Mozilla Persona account required.

* Registered connections are viewable in the ``node`` couchdb database. To disable a registered connection, set the active key to false, or just delete the document describing the connection.
  
* You must restart the LR Service to apply any changes that were made to the distribution policy. This includes:

	- Registering new nodes to the distribute list.
	- Removing existing node from the distribute list, either via disabling or by deletion.
	  

Setting up a node as a destination for distribution
===================================================

* when setting up your node, answer ``T`` for the question: ``Does the node want to be the destination for replication (T/F)?``
* Register for distribution on the source node: ``http://<sourceNodePublicAddress>/register``

    - a Mozilla Persona account is required to verify your identity.
    - Default destination URL on your node is ``http://yourNodesPublicAddress/incoming``

        + this will be checked when you submit the form.
        + Username and Password in the registration form are for the CouchDB admin account on your node

            * This will not be checked when you submit the form.

* Ask the node administrator to restart the LR service on their node to load the new distribute connection. Wait until the distribute service runs to see the replicated documents on your node.


Outstanding Questions/Issues
============================

* Can/Should we remove the necessity to restart the LR service to apply changes to distribution connections? 
  
  	- Some historical reasoning on GitHub: https://github.com/LearningRegistry/LearningRegistry/issues/276 

* How do documents go from incoming to the resource_data database? 
  
    - Issue report: https://github.com/LearningRegistry/LearningRegistry/issues/275
    - There is an issue with uwsgi versions.  Newer versions need to have the LR startup script modified in order to support multi-threading. See the ``/etc/init.d/learningregistry`` script within the GitHub source for details.
    

* Distribute service returns an empty error when no connections to distribute to 

	- Issue report: https://github.com/LearningRegistry/LearningRegistry/issues/274	

* What is the distributeResourceDataUrl parameter used for? This is separate from the incoming destination URL (distributeIncomingUrl). In the setup script, the question is posed as… Enter distribute/replication resource_data destination URL (this is the resource_data URL that another node couchdb will use to replicate/distribute to this node).

	- As Distribute relies heavily upon CouchDB to function, CouchDB needs to know the public endpoint of the node which can be read by the destiation node.  It's possible to configure the node such that resource_data and incoming CouchDB databases are made available via a different URL, hence the need to prompt for ``distributeResourceDataUrl`` and ``distributeIncomingUrl`` respectively.

* Can you register and distribute to a node that has “Admin Party” enabled (no admin username or password)?

    - Yes, but this is not recommended as anyone who can access the CouchDB will have full read/write/modify permissions to the incoming DB.
    
* What happens when the supported schema version numbers don’t match between source and destination? Will v0.51 documents be accepted by v0.49 nodes?

    - v0.49 nodes will reject v0.51 documents.
    - v0.51 nodes will accept all current and legacy documents verions, v0.51 and prior. 
