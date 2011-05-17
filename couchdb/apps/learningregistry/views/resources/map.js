function(doc) {
  if (doc.doc_type == 'resource_data_timestamp'){
      emit(doc.doc_ID, {_id: doc.doc_ID, 
                                    'timestamp':{'node_timestamp':doc.node_timestamp}});
  }  
}
