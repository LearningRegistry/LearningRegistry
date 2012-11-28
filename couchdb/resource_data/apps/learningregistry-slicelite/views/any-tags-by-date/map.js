function(doc) {
  if (doc.doc_type != "resource_data" || !doc.node_timestamp) return;
  var node_timestamp = Math.floor(Date.parse(doc.node_timestamp)/1000);
  for(var i in doc.keys){
    emit([doc.keys[i].toLowerCase(), node_timestamp], null);
  }
}