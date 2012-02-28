function(head, req) {
    var row;
    while (row = getRow()) {
        if (row.id.match(/^_design\//) && doc.value.views) {
            for (var viewname in doc.views) {
                if (doc.views[viewname]["data-service"]) {
                    emit([doc.id, viewname], doc.views[viewname]["data-service"]);
                }
            } 

        }
    }
}