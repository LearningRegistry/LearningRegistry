function(doc) {
  if (doc.doc_type == 'resource_data_timestamp'){
      emit(doc.resource_doc_id, {_id: doc.resource_doc_id, 
                                    'timestamp':{'node_timestamp':doc.node_timestamp}});
  }  
}
