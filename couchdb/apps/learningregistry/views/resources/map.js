function(doc) {
  if (doc.doc_type){
      emit(doc.id,null);
  }  
}
