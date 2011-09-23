function(doc) {
  if (doc.doc_type == 'resource_data'){
      emit(doc.doc_type, 1);
  }  
}
