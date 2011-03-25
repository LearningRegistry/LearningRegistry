function(doc) {
  if (doc._id.match(/.*TEST-DATA.*/)) {
	  emit(doc._id, doc);
  }
}