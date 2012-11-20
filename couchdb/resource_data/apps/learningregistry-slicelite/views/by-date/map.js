function(doc) {
  if (doc.doc_type != "resource_data" || !doc.node_timestamp) return;
  var node_timestamp = Math.floor(Date.parse(doc.node_timestamp)/1000);
  emit(node_timestamp,null);
}