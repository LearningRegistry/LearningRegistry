function(doc) {
  if (doc.doc_type != "resource_data" || !doc.node_timestamp) return;
    var node_timestamp = Math.floor(Date.parse(doc.node_timestamp)/1000);
    var sent = [];
    if(doc.identity) {
        if(doc.identity.submitter && sent.indexOf(doc.identity.submitter.toLowerCase()) < 0) {
            sent.push(doc.identity.submitter.toLowerCase());
            emit([doc.identity.submitter.toLowerCase(), node_timestamp], null);
        }
        if(doc.identity.curator && sent.indexOf(doc.identity.curator.toLowerCase()) < 0) {
            sent.push(doc.identity.curator.toLowerCase());
            emit([doc.identity.curator.toLowerCase(), node_timestamp], null);
        }
        if(doc.identity.owner && sent.indexOf(doc.identity.owner.toLowerCase()) < 0) {
            sent.push(doc.identity.owner.toLowerCase());
            emit([doc.identity.owner.toLowerCase(), node_timestamp], null);
        }
        if(doc.identity.signer && sent.indexOf(doc.identity.signer.toLowerCase()) < 0) {
            sent.push(doc.identity.signer.toLowerCase());
            emit([doc.identity.signer.toLowerCase(), node_timestamp], null);
        }
    }
}