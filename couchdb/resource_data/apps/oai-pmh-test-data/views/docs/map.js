function(doc) {
  if (doc._id.match(/.*TEST-DATA.*/) && doc.node_timestamp) {
	  emit(doc._id, doc);
  }
}