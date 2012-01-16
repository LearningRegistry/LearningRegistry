function(doc) {

	if (doc.doc_type != "resource_data" || !doc.node_timestamp) return;
	
	var date_stamp = doc.node_timestamp;
	date_stamp = date_stamp.substring(0,10);
	var identities = new Array();
	
	var arrayContains = function(testArray, testValue) {
		for each(var val in testArray) {
			if(val==testValue) return true;
		}
		return false;
	}	
	
	
	//grab all the identities in identity or submitter/curator/owner/signer (depending on version)
	//if any identities are identical, ignore redundant ones.
	if(doc.identity) {
		if(doc.identity.submitter) {
			identities.push(doc.identity.submitter.toLowerCase());
		}
		if(doc.identity.curator) {
			var curator = doc.identity.curator.toLowerCase();
			if(!arrayContains(identities,curator)) {
				identities.push(curator);
			}
		}
		if(doc.identity.owner) {
			var owner = doc.identity.owner.toLowerCase();
			if(!arrayContains(identities,owner)) {
				identities.push(owner);
			}
		}
		if(doc.identity.signer) {
			var signer = doc.identity.signer.toLowerCase();
			if(!arrayContains(identities,signer)) {
				identities.push(signer);
			}
		}
	}
	if(doc.submitter) {
		var submitter = doc.submitter.toLowerCase();
		if(!arrayContains(identities,submitter)) {
			identities.push(submitter);
		}
	} 
	

	//build identities indices
	for each(identity in identities) {
		emit({'id':identity}, null);
	}
	
	//build date indices
	emit({'date':date_stamp}, null);
	for each(identity in identities) {
		emit([{'date':date_stamp}, {'id':identity}], null);
	}
	
	//build
	var emitaAllKeywordIndices = function(value) {
		emit({'tag':value}, null);
		for each(identity in identities) {
			emit([{'id':identity}, {'tag':value}], null);
		}
		emit([{'date':date_stamp}, {'tag':value}], null);
		for each(identity in identities) {
			emit([{'date':date_stamp}, {'id':identity}, {'tag':value}], null);
		}
	}

	var usedKeys = new Array();
	for each(var key in doc.keys) {
		var cleanKey = key.toLowerCase();
		cleanKey = cleanKey.replace(/^\s+/, "");
		cleanKey = cleanKey.replace(/\s+$/, "");
		//var used = arrayContains(usedKeys, key);
		if(!arrayContains(usedKeys, cleanKey)) {
			emitaAllKeywordIndices(cleanKey);
			usedKeys.push(cleanKey);
		}
		
	  }
	
	for each(var schema in doc.payload_schema) {
		emitaAllKeywordIndices(schema.toLowerCase());
	}
	
	if(doc.resource_data_type) emitaAllKeywordIndices(doc.resource_data_type.toLowerCase());
	
}