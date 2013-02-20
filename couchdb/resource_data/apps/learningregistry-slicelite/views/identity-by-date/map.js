function(doc) {
  if (doc.doc_type != "resource_data" || !doc.node_timestamp) return;
  var node_timestamp = Math.floor(Date.parse(doc.node_timestamp)/1000);
	if(doc.identity) {
		if(doc.identity.submitter) {
			emit([doc.identity.submitter.toLowerCase(), node_timestamp], null);
		}
		if(doc.identity.curator) {
			emit([doc.identity.curator.toLowerCase(), node_timestamp], null);
		}
		if(doc.identity.owner) {
			emit([doc.identity.owner.toLowerCase(), node_timestamp], null);
		}
		if(doc.identity.signer) {
			emit([doc.identity.signer.toLowerCase(), node_timestamp], null);
		}
	}
}