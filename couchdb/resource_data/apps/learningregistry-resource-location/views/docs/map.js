function(doc) {
    if(doc.doc_type == 'resource_data'){
        if (Object.prototype.toString.call( doc.resource_locator ) === '[object Array]') {
            for (i=0; i<doc.resource_locator.length; i++) {
                emit(decodeURI(doc.resource_locator[i]),  null);  
            }
        } else {
            emit(decodeURI(doc.resource_locator),  null);  
        }
    }
}
