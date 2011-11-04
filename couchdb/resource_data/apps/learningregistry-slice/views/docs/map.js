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
	if(doc.identity) {
		if(doc.identity.submitter) identities.push(doc.identity.submitter.toLowerCase());
		if(doc.identity.curator) identities.push(doc.identity.curator.toLowerCase());
		if(doc.identity.owner) identities.push(doc.identity.owner.toLowerCase());
		if(doc.identity.signer) identities.push(doc.identity.signer.toLowerCase());
	}
	if(doc.submitter) identities.push(doc.submitter.toLowerCase());
	

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
		emitaAllKeywordIndices(schema);
	}
	
	if(doc.resource_data_type) emitaAllKeywordIndices(doc.resource_data_type);
	
}