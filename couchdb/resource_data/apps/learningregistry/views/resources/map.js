function(doc) {
  if (doc.doc_type == 'resource_data'){
      emit(doc.doc_ID, null);
  }  
}
