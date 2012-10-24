function(doc) {
	if (doc.doc_type != "resource_data" || !doc.node_timestamp) return;
	var node_timestamp = Math.floor(Date.parse(doc.node_timestamp)/1000);
	if(doc.identity) {
		if(doc.identity.submitter) {
			emit(doc.identity.submitter.toLowerCase());
			emit([doc.identity.submitter.toLowerCase(),node_timestamp]);
		}
		if(doc.identity.curator) {
			emit(doc.identity.curator.toLowerCase());
				emit([doc.identity.curator.toLowerCase(),node_timestamp]);
		}
		if(doc.identity.owner) {
			emit(doc.identity.owner.toLowerCase());
			emit([doc.identity.owner.toLowerCase(),node_timestamp]);
		}
		if(doc.identity.signer) {
			emit(doc.identity.signer.toLowerCase());
			emit([doc.identity.signer.toLowerCase(),node_timestamp]);
		}
	}
	for(var key in doc.keys) {
		var cleanKey = key[key].toLowerCase();
		cleanKey = cleanKey.replace(/^\s+/, "");
		cleanKey = cleanKey.replace(/\s+$/, "");
		emit(cleanKey);
		emit([cleanKey,node_timestamp]);
	}

}