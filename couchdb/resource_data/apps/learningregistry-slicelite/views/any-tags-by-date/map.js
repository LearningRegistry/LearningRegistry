function(doc) {
  if (doc.doc_type != "resource_data" || !doc.node_timestamp) return;
  var node_timestamp = Math.floor(Date.parse(doc.node_timestamp)/1000);
  var sent_keys = [];
  for(var i in doc.keys){
    if(sent_keys.indexOf(doc.keys[i].toLowerCase()) < 0)
    {
       sent_keys.push(doc.keys[i].toLowerCase());
       emit([doc.keys[i].toLowerCase(), node_timestamp], null);
    }
  }
  for(i in doc.payload_schema){
    if(sent_keys.indexOf(doc.payload_schema[i].toLowerCase()) < 0)
    {
       sent_keys.push(doc.payload_schema[i].toLowerCase());
       emit([doc.payload_schema[i].toLowerCase(), node_timestamp], null);
    }
  }
}